#!/usr/bin/env python3
"""Seed Chinese translations for high-frequency nodes into dict/nodes.descriptions.zh.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DICT_PATH = ROOT / "dict" / "nodes.descriptions.zh.json"

# node -> zh description; flubs: name -> zh or {desc, values:{}}
SAMPLES: dict = {
    "Mountain": {
        "zh": "Mountain 是 Gaea 最通用的基础形体之一：以调制 Voronoi 与扭曲生成接近真实的山地形态，便于继续修饰与侵蚀。",
        "flubs": {
            "Scale": "控制山脉整体尺度与范围。数值越大，山体越宽广。",
            "Height": "设置山脉最大海拔，决定峰顶相对高度。",
            "Style": "指定山脉的地质/视觉风格，影响外形与表面特征。",
            "Bulk": "控制山体体量：偏瘦或厚重。",
            "Reduce Details": "减少细碎表面细节，使山体更平滑、更抽象。",
            "Seed": "随机种子，用于生成不同变体；其它参数不变时仅改变形态细节。",
        },
        "values": {
            "Style": {
                "Basic": "生成简洁、少侵蚀感的基础山脉。",
                "Eroded": "施加侵蚀感，轮廓更自然。",
                "Old": "模拟古老山地：棱角软化、形态更圆润。",
            },
            "Bulk": {
                "Low": "较纤细、体量感较弱的山脉。",
                "Medium": "体量适中、通用的折中设置。",
                "High": "厚重、体量大的山脉。",
            },
        },
    },
    "Ridge": {
        "zh": "Ridge 生成带多处断裂与剪切感的崎岖山脊线。",
        "flubs": {
            "Scale": "山脊线的尺度。",
            "Height": "设置山脊高度。",
            "Definition": "增强脊线上的细节。",
            "Seed": "节点过程的随机种子。",
            "Scale X": "X 轴非均匀缩放。",
            "Scale Y": "Y 轴非均匀缩放。",
        },
    },
    "Perlin": {
        "zh": "Perlin 是最基础的噪声。Gaea 提供面向地形设计的“地理变体”，从一开始就更适合做地貌。",
        "flubs": {
            "Type": "指定 Perlin 噪声风格，影响整体外观。",
            "Noise": "指定 Perlin 噪声风格，影响整体外观。",
            "Scale": "噪声尺度。越大形状越粗、细节越少；越小细节越密。",
            "Octaves": "噪声倍频数。越高通过叠加更多层细节而更复杂。",
            "Gain": "控制倍频之间的振幅衰减，影响细节持续强度。",
            "Height": "设置噪声最大高度/强度，垂直缩放输出。",
            "Seed": "随机种子。",
        },
    },
    "Erosion2": {
        "zh": "高级水力侵蚀节点，可产生更细致、更真实的侵蚀结果。",
        "flubs": {
            "Duration": "控制侵蚀运行时长。时间越长，地貌变化越丰富。",
            "General": "控制侵蚀运行时长。时间越长，地貌变化越丰富。",
            "Downcutting": "控制水流下切深度，塑造河谷与沟槽。",
            "Erosion Scale": "设置侵蚀特征的整体尺度：从细沟到巨大沟壑。",
            "Seed": "在其它设置不变时随机化侵蚀图案。",
            "Sediment Discharge": "细而轻的沉积物：可输送较远并填充沟谷细节。",
        },
    },
    "Adjust": {
        "zh": "将常用高度/数值调整集中在一个节点中，并可单独开关各项处理（又称 Fx）。",
        "flubs": {
            "Multiply": "将每个值乘以指定系数。",
            "Shaper": "用塑形函数改变数值曲线。",
            "Clamp": "将数值限制在指定最小/最大范围。",
            "Clip": "裁切超出给定范围的数值。",
            "Drop": "按阈值丢弃偏低或偏高的值。",
            "Autolevel": "自动拉伸数值以占满可用输出范围。",
        },
    },
    "Combine": {
        "zh": "Combine 是最重要的节点之一：用多种数学/混合模式合并两个地形（或任意输出）。",
        "flubs": {
            "Ratio": "应用于所选混合方式的比例。",
            "Mode": "混合模式。",
            "Output": "如何处理数据范围。",
            "Swap Inputs": "交换两个输入。",
            "Enhance": "对输出做后处理。",
        },
        "values": {
            "Mode": {
                "Blend": "将源简单叠在底之上，无额外运算。",
                "Add": "相加提亮：源加到底上。",
                "Screen": "类似投影到屏幕的滤色提亮混合。",
            },
            "Output": {
                "None": "保留未钳制的原始数据；进阶有用但更不安全。",
                "Clamp": "钳制到 0..1；稍慢但一般更推荐。",
                "Extend": "扩展以填满范围。",
            },
            "Enhance": {
                "None": "无后处理（推荐）。",
                "Autolevel": "自动电平输出。",
                "Equalize": "均衡化输出。",
            },
        },
    },
    "Clamp": {
        "zh": "Clamp 控制地形高度：可压缩、在特定高度裁切，或用 Extend 拉高。",
        "flubs": {
            "Mode": "限制数值所用的钳制方式。",
            "Value": "钳制阈值/范围；超出部分被限制在边界。",
            "Drop": "将整体形状降到最低值，即“放下”整个形体。",
        },
        "values": {
            "Mode": {
                "Standard": "对输入施加固定最小/最大钳制。",
                "Normalized": "钳制并重映射到归一化 0–1 范围。",
            },
        },
    },
    "Blur": {
        "zh": "Blur 扩散锐利形状并软化地形。",
    },
    "Autolevel": {
        "zh": "自动将输入重映射，以占满可用的高度或遮罩范围。",
    },
    "Snow": {
        "zh": "模拟降雪、融雪与沉降，并控制积雪如何附着与沿地形流动。",
        "flubs": {
            "Duration": "积雪累积时间，影响整体雪量。",
            "Snow": "积雪累积时间，影响整体雪量。",
            "Intensity": "降雪与堆积速率，影响厚度。",
            "Settle Duration": "新雪沉降压实所需时间。",
            "Melt": "融雪方式，影响融雪图案与分布。",
            "Melt Type": "融雪方式，影响融雪图案与分布。",
        },
        "values": {
            "Melt Type": {
                "Uniform": "全图均匀融雪。",
                "Directional": "沿特定方向优先融雪。",
            },
        },
    },
    "Thermal": {
        "zh": "模拟热力侵蚀，生成岩屑坡（talus）与碎屑堆积。",
        "flubs": {
            "Duration": "热力侵蚀作用时长。越高变化越明显。",
            "Erosion": "热力侵蚀作用时长。越高变化越明显。",
            "Strength": "热力侵蚀强度。",
            "Anisotropy": "侵蚀与沉积的方向性偏差。",
            "Seed": "随机化侵蚀图案。",
            "Talus": "物质开始下滑形成岩屑坡的最大坡角。",
        },
    },
    "Height": {
        "zh": "按指定高度范围生成选择遮罩。",
        "flubs": {
            "Range": "纳入遮罩的最小/最大海拔。",
            "Falloff": "范围边界过渡柔和度。越高越平滑。",
        },
    },
    "Slope": {
        "zh": "按指定坡度范围生成选择遮罩。",
        "flubs": {
            "Range": "纳入的最小/最大坡角。",
            "Falloff": "范围边界的柔和过渡。",
            "Type": "坡度计算方式，影响遮罩分布。",
            "Micro Accent": "增强坡度遮罩中的细微变化。",
        },
        "values": {
            "Type": {
                "Accurate": "更精确的坡度计算，细节更真实。",
                "Normalized": "在坡度范围内更均匀一致的分布。",
            },
        },
    },
    "Sandstone": {
        "zh": "生成层状砂岩式阶地与沉积岩结构。",
        "flubs": {
            "Passes": "模拟层状砂岩的侵蚀遍数。",
            "Iterations": "每遍内侵蚀过程重复次数。",
            "Spacing": "砂岩层间距，影响层理频率。",
            "Intensity": "砂岩效果整体强度。",
            "Convexity": "岩层曲率，更圆或更平。",
            "Tilt": "岩层倾斜角，模拟地质掀斜。",
        },
    },
    "SatMap": {
        "zh": "用可控范围与处理，从卫星风格预设色板生成地形颜色。",
    },
    "Canyon": {
        "zh": "快速且细致的峡谷基础体：基于排水生成河谷型峡谷。",
        "flubs": {
            "Style": "峡谷造型模型，影响形态与壁面特征。",
            "Structure": "峡谷造型模型，影响形态与壁面特征。",
            "Scale": "峡谷尺度。",
            "Slot": "窄缝峡谷成分：更深切缝的紧度与强调。",
            "Valley": "更宽阔的谷地形态。",
            "Surrounding": "峡谷与周围地形的融合程度。",
        },
        "values": {
            "Style": {
                "Classic": "干净、程序化的切削剖面。",
                "Eroded": "增加侵蚀破碎与自然不规则感。",
                "Eroded2": "更丰富的壁面细节与侵蚀感。",
            },
        },
    },
    "Crater": {
        "zh": "陨石坑基础体，可生成多种坑体形态。",
        "flubs": {
            "Style": "坑体外观与造型方法。",
            "Scale": "坑体整体大小。",
            "Formation": "形成特征：深度、宽度等。",
            "Height": "相对底面的最大凸起/高度。",
            "Rim": "坑缘锐利度与剖面。",
            "Shape": "坑体外轮廓。",
        },
        "values": {
            "Style": {
                "New": "现代算法，形态更丰富。",
                "Classic": "经典旧式风格。",
            },
            "Rim": {
                "Soft": "缓和、偏风化的坑缘。",
                "Sharp": "陡峭清晰的新鲜坑缘。",
            },
        },
    },
    "Constant": {
        "zh": "生成指定高度的空白地形，或平坦颜色输出。",
        "flubs": {
            "Output": "输出类型。",
            "Constant": "输出类型。",
            "Height": "空白地形的高度。",
            "Color": "平坦颜色输出所用颜色。",
        },
        "values": {
            "Output": {
                "Height": "创建指定高度的平坦地形。",
                "Color": "创建指定颜色的平坦颜色输出。",
            },
        },
    },
    "Accumulator": {
        "zh": "从场景中可用节点累积特定类型的图，例如水、森林或雪。",
    },
    "AO": {
        "zh": "环境光遮蔽（Ambient Occlusion），增强凹处阴影感。",
    },
    "Angle": {
        "zh": "按朝向/角度条件生成遮罩或影响。",
    },
    "Cellular": {
        "zh": "蜂窝/细胞噪声，适合岩石破裂与斑块状分布。",
    },
    "Cartography": {
        "zh": "制图风格处理，用于地图化表现。",
    },
    "Bomber": {
        "zh": "在地形上散布/“轰炸”放置多种细节或实例效果。",
    },
    "BlobRemover": {
        "zh": "移除孤立斑块/碎块，清理遮罩或地形噪点。",
    },
    "Aperture": {
        "zh": "光圈/开口相关控制，用于局部通行或造型。",
    },
    "Anastomosis": {
        "zh": "模拟辫状/网状水系连通结构。",
    },
    "Bulbous": {
        "zh": "生成圆鼓、块状的岩石/地貌体量。",
    },
    "CLUTer": {
        "zh": "颜色查找表（CLUT）映射，用于风格化上色。",
    },
    "Clip": {
        "zh": "裁切超出范围的数值。",
    },
    "Chokepoint": {
        "zh": "强调或塑造狭窄通道/咽喉地形。",
    },
    "ColorErosion": {
        "zh": "结合颜色通道的侵蚀/沉积染色效果。",
    },
}


def apply_values(flub_entry: dict, value_map: dict) -> int:
    n = 0
    values = flub_entry.setdefault("values", {})
    for vname, vzh in value_map.items():
        if vname not in values:
            values[vname] = {"en": "", "zh": vzh}
            n += 1
        else:
            values[vname]["zh"] = vzh
            n += 1
    return n


def main() -> None:
    data = json.loads(DICT_PATH.read_text(encoding="utf-8"))
    nodes = data["nodes"]
    filled_nodes = 0
    filled_fields = 0

    for name, sample in SAMPLES.items():
        if name not in nodes:
            print(f"skip missing node: {name}")
            continue
        node = nodes[name]
        if sample.get("zh"):
            node["zh"] = sample["zh"]
            filled_fields += 1
        flubs = node.setdefault("flubs", {})
        for fname, fzh in (sample.get("flubs") or {}).items():
            if fname not in flubs:
                flubs[fname] = {"en": "", "zh": fzh}
            else:
                flubs[fname]["zh"] = fzh
            filled_fields += 1
        for fname, vmap in (sample.get("values") or {}).items():
            if fname not in flubs:
                flubs[fname] = {"en": "", "zh": "", "values": {}}
            filled_fields += apply_values(flubs[fname], vmap)
        filled_nodes += 1

    DICT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {DICT_PATH}")
    print(f"Nodes seeded: {filled_nodes}, fields written: {filled_fields}")


if __name__ == "__main__":
    main()
