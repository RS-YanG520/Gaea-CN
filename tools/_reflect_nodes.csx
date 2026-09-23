using System;
using System.Linq;
using System.Reflection;

var path = @"D:\Program Files\Gaea 2\Gaea.Nodes.dll";
var asm = Assembly.LoadFrom(path);
Console.WriteLine(asm.FullName);

Type? Find(string name) =>
    asm.GetTypes().FirstOrDefault(t => t.Name == name || t.FullName == name);

foreach (var n in new[] { "Mountain", "Erosion2", "Combine" })
{
    var t = Find(n);
    Console.WriteLine($"\n=== {n}: {(t?.FullName ?? "NOT FOUND")} ===");
    if (t is null) continue;
    Console.WriteLine("Base: " + t.BaseType?.FullName);
    foreach (var a in t.GetCustomAttributes(true))
        Console.WriteLine("Attr: " + a.GetType().FullName + " | " + a);
}
