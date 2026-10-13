using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

/// <summary>
/// Drop-in style launcher (can replace Gaea.exe after backup to Gaea.real.exe).
/// Sets DOTNET_STARTUP_HOOKS then starts the real Gaea binary — same UX idea as 星空汉化.
/// </summary>
internal static class Program
{
    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    private static extern int MessageBoxW(IntPtr hWnd, string text, string caption, uint type);

    [STAThread]
    private static int Main(string[] args)
    {
        try
        {
            var self = Environment.ProcessPath
                       ?? Path.Combine(AppContext.BaseDirectory, "GaeaCn.Launcher.exe");
            var dir = Path.GetDirectoryName(self) ?? AppContext.BaseDirectory;

            var real = ResolveRealGaea(dir);
            if (real is null)
            {
                Fail("找不到原版 Gaea。请确认同目录有 Gaea.real.exe，或先运行 tools\\install_gaea_cn.ps1。");
                return 1;
            }

            var hook = ResolveHookDll(dir);
            if (hook is null)
            {
                Fail("找不到 GaeaCn.StartupHook.dll。请先运行 tools\\install_gaea_cn.ps1。");
                return 2;
            }

            var psi = new ProcessStartInfo
            {
                FileName = real,
                WorkingDirectory = Path.GetDirectoryName(real) ?? dir,
                UseShellExecute = false,
            };
            foreach (System.Collections.DictionaryEntry kv in Environment.GetEnvironmentVariables())
            {
                var k = kv.Key?.ToString();
                if (string.IsNullOrEmpty(k)) continue;
                psi.Environment[k] = kv.Value?.ToString() ?? "";
            }

            var prev = psi.Environment.TryGetValue("DOTNET_STARTUP_HOOKS", out var existing)
                ? existing
                : "";
            psi.Environment["DOTNET_STARTUP_HOOKS"] = string.IsNullOrWhiteSpace(prev)
                ? hook
                : hook + Path.PathSeparator + prev;

            foreach (var a in args)
                psi.ArgumentList.Add(a);

            Process.Start(psi);
            return 0;
        }
        catch (Exception ex)
        {
            Fail("Gaea-CN 启动失败：\n" + ex.Message);
            return 99;
        }
    }

    private static string? ResolveRealGaea(string dir)
    {
        foreach (var name in new[] { "Gaea.real.exe", "Gaea.original.exe", "Gaea.bak.exe" })
        {
            var p = Path.Combine(dir, name);
            if (File.Exists(p)) return p;
        }

        var selfName = Path.GetFileName(Environment.ProcessPath ?? "");
        var gaea = Path.Combine(dir, "Gaea.exe");
        if (File.Exists(gaea) &&
            !selfName.Equals("Gaea.exe", StringComparison.OrdinalIgnoreCase))
            return gaea;

        return null;
    }

    private static string? ResolveHookDll(string gaeaDir)
    {
        var local = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "Gaea-CN", "GaeaCn.StartupHook.dll");
        foreach (var c in new[]
                 {
                     Path.Combine(gaeaDir, "GaeaCn", "GaeaCn.StartupHook.dll"),
                     local,
                 })
            if (File.Exists(c)) return c;
        return null;
    }

    private static void Fail(string text)
    {
        try
        {
            var logDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "Gaea-CN");
            Directory.CreateDirectory(logDir);
            File.AppendAllText(
                Path.Combine(logDir, "launcher.exe.log"),
                $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] {text}\n",
                Encoding.UTF8);
        }
        catch { /* ignore */ }

        try { MessageBoxW(IntPtr.Zero, text, "Gaea-CN", 0x10); }
        catch { /* ignore */ }
    }
}
