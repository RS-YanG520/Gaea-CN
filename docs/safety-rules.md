# 安全红线

本项目只做**显示层**汉化，不得改变工程文件中的标识符语义。

## 禁止修改 / 禁止写成中文

| 位置 | 字段 | 原因 |
|------|------|------|
| `.terrain` | `$type` | 反序列化类型名 |
| `.terrain` | 属性键（如 `Downcutting`） | JSON 属性名绑定 C# 属性 |
| `.terrain` | 枚举字符串（如 `"Bulk": "High"`） | 枚举值按英文名读写 |
| `.terrain` | 端口 `Name`（`In`/`Out`/…） | 图连接与导出依赖 |
| `.terrain` | 节点实例 `Name`（默认类型名） | 用户可改名；默认应保持英文类型名 |
| `Nodes.json` | 顶层节点 `Name` | 工具箱 ID、收藏夹、默认实例名 |
| `Nodes.json` | `Type: EnumValue` 的 `Name` | 写入工程的枚举值 |
| `Nodes.json` | 与序列化属性同名的 `Flub.Name` | 可能参与属性面板绑定键 |
| `User.options` 等 | Favorites 列表 | 英文节点 ID |

## 允许修改

- 任意 `Description`（节点说明、参数说明、枚举说明）
- 纯 UI 文案（菜单、对话框、快捷键文档）——后续阶段经显示层注入
- 展示用标签：通过 en→zh 词典覆盖显示，**不改**持久化键

## 操作约定

1. 修改安装目录前必须先备份到 `backups/`。
2. 只覆盖 `Resources\Nodes.json`（阶段 1），不要改 DLL / `.terrain` 示例。
3. Gaea 升级后先 `restore`，再重新 `extract` → 翻译 → `build` → `apply`。
4. 验收时对比：打开同一 `.terrain`，节点 `$type` 与关键参数键仍为英文。
