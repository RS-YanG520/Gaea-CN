using System.Collections;
using System.Collections.Concurrent;
using System.IO;
using System.Reflection;
using System.Text.Json;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;

/// <summary>
/// Translates UI by:
/// 1) TextBlock / Button Content (already-visible text)
/// 2) DataContext string properties (fixes left-rail categories that only
///    materialize TextBlocks when selected — the click-to-translate bug)
/// </summary>
internal sealed class StartupHook
{
    public static void Initialize()
    {
        try { SafeUiTranslator.Start(); }
        catch (Exception ex) { SafeUiTranslator.Log("Initialize failed: " + ex); }
    }
}

internal static class SafeUiTranslator
{
    private static readonly ConcurrentDictionary<string, string> Map = new(StringComparer.Ordinal);
    private static readonly ConcurrentDictionary<string, byte> LoggedTypes = new(StringComparer.Ordinal);
    private static int _started;
    private static int _hits;
    private static int _vmHits;
    private static long _lastClickSweep;
    private static DispatcherTimer? _pulse;

    /// <summary>
    /// Exact tokens used as icon-font / geometry keys in the right-rail toolbar.
    /// Translating these blanks the glyph (e.g. Sun → 太阳).
    /// Longer phrases like "Sun Azimuth" remain translatable.
    /// </summary>
    // Case-sensitive: lowercase tokens from 星空 00_PROTECTED are icon resource keys;
    // Title Case "Sun"/"Histogram" may be real UI labels and should still translate.
    // Keep a few Title Case toolbar glyph keys that Gaea uses as icon TextBlocks.
    private static readonly HashSet<string> IconGlyphKeys = new(StringComparer.Ordinal)
    {
        "Sun", "Light", "Dark", "Grid", "Camera", "Sphere", "Water", "Sky", "Moon",
        "Engine", "World", "Earth", "View", "Viewport", "Render", "Clay", "Mask",
        "Overlay", "Compass", "Bounds", "Navigate", "Screenshot", "Capture",
    };

    private static bool IsIconGlyphKey(string? s) =>
        !string.IsNullOrEmpty(s) && IconGlyphKeys.Contains(s);

    public static void Start()
    {
        if (Interlocked.Exchange(ref _started, 1) == 1) return;
        LoadDictionary();
        Task.Run(WaitAndInstall);
    }

    private static void LoadDictionary()
    {
        try
        {
            var asmDir = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location) ?? "";
            var local = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Gaea-CN");
            var repoDict = Path.GetFullPath(Path.Combine(asmDir, "..", "..", "dict"));

            // Merge every available source (JSON + 星空-style txt folders)
            foreach (var jsonPath in new[]
                     {
                         Path.Combine(asmDir, "ui.display.zh.json"),
                         Path.Combine(local, "ui.display.zh.json"),
                         Path.Combine(repoDict, "ui.display.zh.json"),
                     })
                LoadJsonMap(jsonPath);

            foreach (var dir in new[]
                     {
                         Path.Combine(asmDir, "zh-dict"),
                         Path.Combine(local, "zh-dict"),
                         Path.Combine(repoDict, "xingkong"),
                     })
                LoadTxtDictFolder(dir);

            foreach (var prot in new[]
                     {
                         Path.Combine(asmDir, "ui.protected.json"),
                         Path.Combine(local, "ui.protected.json"),
                         Path.Combine(repoDict, "ui.protected.json"),
                     })
                LoadProtectedKeys(prot);

            Log($"Dictionary ready: map={Map.Count} iconKeys={IconGlyphKeys.Count}");
            if (Map.Count == 0) Log("Dictionary not found");
        }
        catch (Exception ex) { Log("LoadDictionary: " + ex.Message); }
    }

    private static void LoadJsonMap(string path)
    {
        if (!File.Exists(path)) return;
        try
        {
            using var doc = JsonDocument.Parse(File.ReadAllText(path));
            var n = 0;
            foreach (var p in doc.RootElement.EnumerateObject())
            {
                if (p.Value.ValueKind != JsonValueKind.String) continue;
                var zh = p.Value.GetString();
                if (string.IsNullOrWhiteSpace(zh)) continue;
                RegisterKey(p.Name, zh!);
                n++;
            }
            Log($"Loaded json entries≈{n} from {path}");
        }
        catch (Exception ex) { Log($"LoadJsonMap {path}: {ex.Message}"); }
    }

    private static void LoadTxtDictFolder(string dir)
    {
        if (!Directory.Exists(dir)) return;
        var n = 0;
        foreach (var file in Directory.EnumerateFiles(dir, "*.txt"))
        {
            try
            {
                foreach (var raw in File.ReadLines(file))
                {
                    var line = raw.Trim();
                    if (line.Length == 0 || line[0] == '#') continue;
                    var eq = line.IndexOf('=');
                    if (eq <= 0) continue;
                    var en = line[..eq].Trim();
                    var zh = line[(eq + 1)..].Trim();
                    if (en.Length == 0 || zh.Length == 0) continue;
                    RegisterKey(en, zh);
                    if (en.Contains('_', StringComparison.Ordinal))
                    {
                        var bare = en.Replace("_", "", StringComparison.Ordinal);
                        if (bare.Length > 0) RegisterKey(bare, zh);
                    }
                    n++;
                }
            }
            catch (Exception ex) { Log($"LoadTxt {file}: {ex.Message}"); }
        }
        if (n > 0) Log($"Loaded txt entries≈{n} from {dir}");
    }

    private static void LoadProtectedKeys(string path)
    {
        if (!File.Exists(path)) return;
        try
        {
            using var doc = JsonDocument.Parse(File.ReadAllText(path));
            if (!doc.RootElement.TryGetProperty("iconGlyphKeys", out var arr)) return;
            foreach (var el in arr.EnumerateArray())
            {
                var s = el.GetString();
                if (!string.IsNullOrWhiteSpace(s))
                    IconGlyphKeys.Add(s!);
            }
            Log($"Loaded protected keys from {path}");
        }
        catch (Exception ex) { Log($"LoadProtectedKeys {path}: {ex.Message}"); }
    }

    private static async Task WaitAndInstall()
    {
        for (var i = 0; i < 200; i++)
        {
            await Task.Delay(200).ConfigureAwait(false);
            if (Application.Current is null) continue;
            await Application.Current.Dispatcher.InvokeAsync(Install).Task.ConfigureAwait(false);
            Log("VM+UI translator installed");
            return;
        }
        Log("Timeout waiting for WPF Application");
    }

    private static void Install()
    {
        EventManager.RegisterClassHandler(typeof(FrameworkElement), FrameworkElement.LoadedEvent,
            new RoutedEventHandler((_, e) =>
            {
                if (e.Source is FrameworkElement fe)
                {
                    var n = TranslateElement(fe);
                    if (n > 0) RefreshNear(fe, 16);
                }
            }), true);

        EventManager.RegisterClassHandler(typeof(MenuItem), MenuItem.SubmenuOpenedEvent,
            new RoutedEventHandler((_, e) =>
            {
                if (e.Source is MenuItem mi)
                {
                    TranslateElement(mi);
                    mi.Dispatcher.BeginInvoke(DispatcherPriority.Loaded, () =>
                    {
                        TranslateElement(mi);
                        RefreshNear(mi, 18);
                        Sweep(mi, 20, 300);
                    });
                }
            }), true);

        EventManager.RegisterClassHandler(typeof(UIElement), UIElement.PreviewMouseLeftButtonUpEvent,
            new MouseButtonEventHandler((_, e) =>
            {
                var now = Environment.TickCount64;
                if (now - _lastClickSweep < 400) return;
                _lastClickSweep = now;
                var disp = Application.Current.Dispatcher;
                disp.BeginInvoke(DispatcherPriority.Background, () => SweepAll("after-click", 26, 500));
            }), true);

        EventManager.RegisterClassHandler(typeof(Window), FrameworkElement.LoadedEvent,
            new RoutedEventHandler((_, e) =>
            {
                if (e.Source is Window w) HookWindow(w);
            }), true);

        foreach (Window w in Application.Current.Windows)
            HookWindow(w);

        SweepAll("install-now", 28, 600);

        _pulse = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(120) };
        var pulses = 0;
        _pulse.Tick += (_, _) =>
        {
            PulsePass();
            pulses++;
            if (pulses == 50) _pulse.Interval = TimeSpan.FromMilliseconds(500);
            if (pulses == 80) _pulse.Interval = TimeSpan.FromSeconds(3);
        };
        _pulse.Start();
    }

    private static void HookWindow(Window w)
    {
        try
        {
            w.ContentRendered -= OnRendered;
            w.ContentRendered += OnRendered;
            w.Activated -= OnActivated;
            w.Activated += OnActivated;
            Sweep(w, 28, 600);
        }
        catch (Exception ex) { Log("HookWindow: " + ex.Message); }
    }

    private static void OnRendered(object? s, EventArgs e)
    {
        if (s is Window w)
        {
            Sweep(w, 28, 600);
            Log($"ContentRendered uiHits={_hits} vmHits={_vmHits}");
        }
    }

    private static void OnActivated(object? s, EventArgs e)
    {
        if (s is Window w) Sweep(w, 24, 400);
    }

    private static void PulsePass()
    {
        try
        {
            var n = 0;
            foreach (Window w in Application.Current.Windows)
                n += Sweep(w, 24, 300);
            if (n > 0) Log($"pulse replaced={n} vmHits={_vmHits}");
        }
        catch { /* ignore */ }
    }

    private static void SweepAll(string tag, int depth, int budget)
    {
        try
        {
            var n = 0;
            foreach (Window w in Application.Current.Windows)
            {
                n += Sweep(w, depth, budget);
                n += SweepOpenPopups(w, depth, budget);
            }
            if (Application.Current.MainWindow is { } mw)
            {
                n += Sweep(mw, depth, budget);
                n += SweepOpenPopups(mw, depth, budget);
            }
            Log($"{tag} replaced={n} uiHits={_hits} vmHits={_vmHits}");
        }
        catch (Exception ex) { Log($"{tag} error: {ex.Message}"); }
    }

    /// <summary>Flyout category menus live in Popup roots outside the normal window walk.</summary>
    private static int SweepOpenPopups(DependencyObject root, int depth, int budget)
    {
        var n = 0;
        var stack = new Stack<DependencyObject>();
        stack.Push(root);
        var seen = 0;
        while (stack.Count > 0 && seen < 400)
        {
            var node = stack.Pop();
            seen++;
            if (node is Popup { IsOpen: true, Child: { } child })
                n += Sweep(child, depth, budget);
            int count;
            try { count = VisualTreeHelper.GetChildrenCount(node); }
            catch { continue; }
            for (var i = 0; i < count; i++)
            {
                try { stack.Push(VisualTreeHelper.GetChild(node, i)); }
                catch { /* skip */ }
            }
        }
        return n;
    }

    private static void RefreshNear(DependencyObject node, int depth)
    {
        try
        {
            var panel = FindAncestor<Panel>(node)
                        ?? FindAncestor<ItemsControl>(node) as DependencyObject
                        ?? VisualTreeHelper.GetParent(node);
            if (panel is null) return;
            var parent = VisualTreeHelper.GetParent(panel) ?? panel;
            Sweep(parent, depth, 120);
        }
        catch { /* ignore */ }
    }

    private static T? FindAncestor<T>(DependencyObject? node) where T : class
    {
        var cur = node;
        for (var i = 0; i < 14 && cur is not null; i++)
        {
            if (cur is T m) return m;
            try { cur = VisualTreeHelper.GetParent(cur); }
            catch { return null; }
        }
        return null;
    }

    private static int Sweep(DependencyObject? root, int maxDepth, int budget)
    {
        if (root is null || budget <= 0) return 0;
        var replaced = 0;
        var stack = new Stack<(DependencyObject node, int depth)>();
        stack.Push((root, 0));
        var visited = 0;
        var seen = new HashSet<int>();

        while (stack.Count > 0 && replaced < budget && visited < budget * 12)
        {
            var (node, depth) = stack.Pop();
            var id = RuntimeHelpersHash(node);
            if (!seen.Add(id)) continue;
            visited++;
            replaced += TranslateElement(node);

            // Also walk ItemsControl logical children (virtualized lists)
            if (node is ItemsControl ic)
            {
                foreach (var item in ic.Items)
                {
                    replaced += TranslateObjectStrings(item, isVm: true);
                    if (item is DependencyObject d)
                        replaced += TranslateElement(d);
                }
            }

            if (depth >= maxDepth) continue;

            // Visual children
            try
            {
                var count = VisualTreeHelper.GetChildrenCount(node);
                for (var i = 0; i < count; i++)
                {
                    try { stack.Push((VisualTreeHelper.GetChild(node, i), depth + 1)); }
                    catch { /* skip */ }
                }
            }
            catch { /* skip */ }

            // Logical children (Inlines / some Actipro labels). Keep narrow to avoid
            // walking unstable custom trees during startup.
            if (node is TextBlock or Panel or Border or ContentControl or ItemsControl)
            {
                try
                {
                    foreach (var child in LogicalTreeHelper.GetChildren(node))
                    {
                        if (child is DependencyObject d)
                            stack.Push((d, depth + 1));
                    }
                }
                catch { /* skip */ }
            }
        }
        return replaced;
    }

    private static int RuntimeHelpersHash(object o) =>
        System.Runtime.CompilerServices.RuntimeHelpers.GetHashCode(o);

    private static int TranslateElement(DependencyObject node)
    {
        var n = 0;
        n += TranslateVisual(node);

        if (node is FrameworkElement fe)
        {
            if (fe.ToolTip is string tip)
                n += SetString(() => tip, v => fe.ToolTip = v);
            if (fe.DataContext is not null)
                n += TranslateObjectStrings(fe.DataContext, isVm: true);
            // Some items put the model in Tag
            if (fe.Tag is not null && fe.Tag is not string)
                n += TranslateObjectStrings(fe.Tag, isVm: true);
        }
        return n;
    }

    private static int TranslateVisual(DependencyObject node)
    {
        switch (node)
        {
            case TextBlock tb when !tb.IsKeyboardFocused:
                return SetString(() => tb.Text, v => tb.Text = v);
            case AccessText at:
                return SetString(() => at.Text, v => at.Text = v);
            case Run run:
                return SetString(() => run.Text, v => run.Text = v);
            case MenuItem mi:
                return SetContent(mi.Header, v => mi.Header = v);
            case TabItem ti:
                return SetContent(ti.Header, v => ti.Header = v);
            case TreeViewItem tvi:
                return SetContent(tvi.Header, v => tvi.Header = v);
            case ListBoxItem lbi:
                return SetContent(lbi.Content, v => lbi.Content = v);
            case Label lbl:
                return SetContent(lbl.Content, v => lbl.Content = v);
            case ButtonBase bb:
                return SetContent(bb.Content, v => bb.Content = v);
            default:
                return 0;
        }
    }

    private static int SetString(Func<string> get, Action<string> set)
    {
        var cur = get();
        if (string.IsNullOrEmpty(cur)) return 0;
        // Skip ultra-short tokens unless they are deliberate UI map entries (In/Out/…)
        if (cur.Length <= 2 && !cur.Contains(' ') && !Lookup(cur, out _))
            return 0;
        if (IsIconGlyphKey(cur)) return 0;
        if (!TryApply(cur, out var zh)) return 0;
        set(zh);
        Interlocked.Increment(ref _hits);
        return 1;
    }

    private static int SetContent(object? content, Action<object?> set)
    {
        switch (content)
        {
            case string s when s.Length <= 2 && !s.Contains(' ') && !Lookup(s, out _):
                return 0;
            case string s when IsIconGlyphKey(s):
                return 0;
            case string s when TryApply(s, out var zh):
                set(zh); Interlocked.Increment(ref _hits); return 1;
            case AccessText at when IsIconGlyphKey(at.Text):
                return 0;
            case AccessText at when at.Text.Length <= 2 && !at.Text.Contains(' ') && !Lookup(at.Text, out _):
                return 0;
            case AccessText at when TryApply(at.Text, out var zhAt):
                at.Text = zhAt; Interlocked.Increment(ref _hits); return 1;
            case TextBlock tb:
                return SetString(() => tb.Text, v => tb.Text = v);
            default:
                return 0;
        }
    }

    /// <summary>Reflect writable string props on view-models (Name/Title/Label/Text/Header/...)</summary>
    private static int TranslateObjectStrings(object? obj, bool isVm)
    {
        if (obj is null || obj is string) return 0;

        // Small collections of category VMs (not DependencyObject trees)
        if (obj is IEnumerable en and not string and not DependencyObject)
        {
            var nCol = 0;
            var i = 0;
            try
            {
                foreach (var item in en)
                {
                    if (item is null || item is DependencyObject) continue;
                    nCol += TranslateObjectStrings(item, isVm: true);
                    if (++i >= 64) break;
                }
            }
            catch { /* ignore */ }
            return nCol;
        }

        // Skip UI elements (already handled via TranslateVisual). Allow other DOs
        // (some Flub/property models inherit DependencyObject).
        if (obj is UIElement or FrameworkContentElement) return 0;

        var n = 0;
        Type type;
        try { type = obj.GetType(); }
        catch { return 0; }

        // Skip framework / BCL types
        var ns = type.Namespace ?? "";
        if (ns.StartsWith("System", StringComparison.Ordinal) ||
            ns.StartsWith("MS.", StringComparison.Ordinal) ||
            ns.StartsWith("Microsoft.", StringComparison.Ordinal))
            return 0;

        var typeName = type.FullName ?? type.Name;

        PropertyInfo[] props;
        try
        {
            props = type.GetProperties(BindingFlags.Instance | BindingFlags.Public);
        }
        catch { return 0; }

        foreach (var p in props)
        {
            try
            {
                if (p.PropertyType != typeof(string)) continue;
                if (!p.CanRead || !p.CanWrite) continue;
                if (p.GetIndexParameters().Length > 0) continue;
                if (!IsDisplayProperty(p.Name)) continue;
                // Name is often an identity key (GraphTab, Flub, Node). Only mutate
                // known display-only category VMs — rewriting GraphTab.Name crashes startup.
                if (p.Name.Equals("Name", StringComparison.OrdinalIgnoreCase) &&
                    !AllowMutateNameProperty(typeName))
                    continue;
                var val = p.GetValue(obj) as string;
                if (string.IsNullOrWhiteSpace(val)) continue;
                // Never rewrite icon/resource-looking tokens on non-tooltip fields
                if (IsIconGlyphKey(val)) continue;
                if (LooksLikeResourceKey(val) && !IsTooltipish(p.Name)) continue;
                if (!TryApply(val, out var zh)) continue;
                p.SetValue(obj, zh);
                n++;
                Interlocked.Increment(ref _vmHits);
                if (LoggedTypes.TryAdd(typeName + ":" + p.Name, 0))
                    Log($"VM translate type={typeName} prop={p.Name} '{val}'→'{zh}'");
            }
            catch
            {
                // ignore non-settable / throw props
            }
        }
        return n;
    }

    /// <summary>Only left-rail / toolbox category chips use Name as pure display text.</summary>
    private static bool AllowMutateNameProperty(string typeName)
    {
        if (typeName.Contains("GraphTab", StringComparison.OrdinalIgnoreCase)) return false;
        if (typeName.Contains("Flub", StringComparison.OrdinalIgnoreCase)) return false;
        if (typeName.Contains(".Engine.", StringComparison.OrdinalIgnoreCase)) return false;
        if (typeName.Contains(".Nodes.", StringComparison.OrdinalIgnoreCase)) return false;
        return typeName.Contains("Category", StringComparison.OrdinalIgnoreCase)
               || typeName.Contains("Toolbox", StringComparison.OrdinalIgnoreCase)
               || typeName.Contains("LibraryGroup", StringComparison.OrdinalIgnoreCase)
               || typeName.Contains("RailItem", StringComparison.OrdinalIgnoreCase)
               || typeName.Contains("NavItem", StringComparison.OrdinalIgnoreCase);
    }

    private static bool IsDisplayProperty(string name)
    {
        // Only mutate human-visible fields — Icon/Glyph/Key/Path etc. must stay English
        return name.Equals("Name", StringComparison.OrdinalIgnoreCase)
               || name.Equals("Title", StringComparison.OrdinalIgnoreCase)
               || name.Equals("Label", StringComparison.OrdinalIgnoreCase)
               || name.Equals("Text", StringComparison.OrdinalIgnoreCase)
               || name.Equals("Header", StringComparison.OrdinalIgnoreCase)
               || name.Equals("Caption", StringComparison.OrdinalIgnoreCase)
               || name.Equals("Description", StringComparison.OrdinalIgnoreCase)
               || name.Equals("DisplayName", StringComparison.OrdinalIgnoreCase)
               || name.Equals("ToolTip", StringComparison.OrdinalIgnoreCase)
               || name.Equals("Tooltip", StringComparison.OrdinalIgnoreCase)
               || name.Equals("Message", StringComparison.OrdinalIgnoreCase)
               || name.Equals("Category", StringComparison.OrdinalIgnoreCase)
               || name.Equals("Group", StringComparison.OrdinalIgnoreCase)
               || name.Equals("GroupName", StringComparison.OrdinalIgnoreCase)
               || name.Equals("Content", StringComparison.OrdinalIgnoreCase)
               || name.EndsWith("Label", StringComparison.OrdinalIgnoreCase)
               || name.EndsWith("Title", StringComparison.OrdinalIgnoreCase)
               || name.EndsWith("Text", StringComparison.OrdinalIgnoreCase)
               || name.EndsWith("Header", StringComparison.OrdinalIgnoreCase)
               || name.EndsWith("Caption", StringComparison.OrdinalIgnoreCase)
               || name.EndsWith("Description", StringComparison.OrdinalIgnoreCase)
               || name.EndsWith("ToolTip", StringComparison.OrdinalIgnoreCase);
    }

    private static bool IsTooltipish(string name) =>
        name.Contains("ToolTip", StringComparison.OrdinalIgnoreCase)
        || name.Contains("Description", StringComparison.OrdinalIgnoreCase)
        || name.Contains("Message", StringComparison.OrdinalIgnoreCase);

    private static bool LooksLikeResourceKey(string val)
    {
        // Phrases we deliberately map are UI copy, never resource keys
        if (Lookup(val, out _)) return false;
        if (IsIconGlyphKey(val)) return true;
        // Paths / dotted resource ids
        if (val.Contains('/') || val.Contains('\\') || val.Contains('.')) return true;
        return false;
    }

    private static void RegisterKey(string key, string zh)
    {
        if (string.IsNullOrWhiteSpace(key)) return;
        Map[key] = zh;
        Map["_" + key] = zh;
        // Category rails often store Title Case but render as ALL CAPS
        var upper = key.ToUpperInvariant();
        if (!string.Equals(upper, key, StringComparison.Ordinal))
            Map[upper] = zh;
        var lower = key.ToLowerInvariant();
        if (!string.Equals(lower, key, StringComparison.Ordinal))
            Map[lower] = zh;
        if (key.Length > 1)
        {
            var title = char.ToUpperInvariant(key[0]) + key[1..].ToLowerInvariant();
            if (!string.Equals(title, key, StringComparison.Ordinal))
                Map[title] = zh;
        }
    }

    private static bool Lookup(string key, out string zh)
    {
        if (Map.TryGetValue(key, out zh!)) return true;
        if (key.Length is > 0 and <= 32)
        {
            if (Map.TryGetValue(key.ToUpperInvariant(), out zh!)) return true;
            if (Map.TryGetValue(key.ToLowerInvariant(), out zh!)) return true;
            if (key.Length > 1)
            {
                var title = char.ToUpperInvariant(key[0]) + key[1..].ToLowerInvariant();
                if (Map.TryGetValue(title, out zh!)) return true;
            }
        }
        zh = "";
        return false;
    }

    private static bool TryApply(string? text, out string zh)
    {
        zh = "";
        if (string.IsNullOrWhiteSpace(text)) return false;
        if (Lookup(text, out zh!))
            return !string.Equals(text, zh, StringComparison.Ordinal);

        var stripped = text.Replace("_", "", StringComparison.Ordinal).Trim();
        if (Lookup(stripped, out zh!))
            return !string.Equals(text, zh, StringComparison.Ordinal);

        // Collapse whitespace/newlines so multi-line tips can match
        var compact = System.Text.RegularExpressions.Regex.Replace(stripped, "\\s+", " ").Trim();
        if (!string.Equals(compact, stripped, StringComparison.Ordinal) &&
            Lookup(compact, out zh!))
            return true;

        var withDots = compact.Replace('\u2026', '.').TrimEnd('.');
        if (Lookup(withDots + "...", out zh!)) return true;
        if (Lookup(withDots + "…", out zh!)) return true;
        if (Lookup(withDots, out zh!)) return true;

        // Dynamic labels: "Bake Selected (2 nodes, 80 MB)"
        if (compact.StartsWith("Bake Selected (", StringComparison.OrdinalIgnoreCase) &&
            Lookup("Bake Selected", out var bakeBase))
        {
            var paren = compact.IndexOf('(');
            zh = bakeBase + " " + compact[paren..];
            return true;
        }
        if (compact.StartsWith("Suspend Engine (", StringComparison.OrdinalIgnoreCase))
        {
            if (compact.Contains("running", StringComparison.OrdinalIgnoreCase))
            {
                zh = "挂起引擎（当前运行中）";
                return true;
            }
            if (compact.Contains("suspended", StringComparison.OrdinalIgnoreCase))
            {
                zh = "恢复引擎（当前已挂起）";
                return true;
            }
        }

        // "Build time: 491 milliseconds" / multi-line with "Status: Built"
        var buildTime = System.Text.RegularExpressions.Regex.Match(
            text, @"Build\s+time:\s*(\d+)\s*milliseconds",
            System.Text.RegularExpressions.RegexOptions.IgnoreCase);
        if (buildTime.Success)
        {
            zh = "构建耗时：" + buildTime.Groups[1].Value + " 毫秒";
            if (System.Text.RegularExpressions.Regex.IsMatch(
                    text, @"Status:\s*Built",
                    System.Text.RegularExpressions.RegexOptions.IgnoreCase))
                zh += "\n状态：已构建";
            return true;
        }
        if (System.Text.RegularExpressions.Regex.IsMatch(
                compact, @"^Status:\s*Built$",
                System.Text.RegularExpressions.RegexOptions.IgnoreCase))
        {
            zh = "状态：已构建";
            return true;
        }

        return false;
    }

    public static void Log(string msg)
    {
        try
        {
            var dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Gaea-CN");
            Directory.CreateDirectory(dir);
            File.AppendAllText(Path.Combine(dir, "startup-hook.log"),
                $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] {msg}\n");
        }
        catch { /* ignore */ }
    }
}
