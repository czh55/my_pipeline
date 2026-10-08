# my_pipeline

把经历沉淀成可复制的步骤章程。

## 底层原则

「如何把大象放进冰箱？开门、放入、关门。」

这句话表面是笑话，背后是人类社会共用的底层原则：**解决问题、做事，都有步骤和章程。**

## 核心警示（必读）

Pipeline 说起来往往简单几步，像菜谱一样「一看就会」——但**菜谱一直存在，饭的味道却千差万别**。

你对一条 pipeline 的感受有多深，取决于你有多少次真实动手实践。它最大的价值在两端：

- **山底**：快速上手，少迷路
- **山顶**：实践够了之后的个人总结

**它不能抄近路把你从山底瞬移到山顶。** 中间必须亲自练。详见 `content/principles.md`。

## 项目结构

```
my_pipeline/
├── content/                 # 真相源（手写 / 随经验追加）
│   ├── principles.md        # 底层原则 + 核心警示
│   └── pipelines/           # 每条 pipeline 一个 YAML
├── schemas/
│   └── pipeline.schema.json
├── scripts/
│   └── render-site.py       # content → docs 静态站
└── docs/                    # GitHub Pages 根目录
```

## 一条 pipeline 长什么样

标准模板见 `content/TEMPLATE.yaml`，字段约定见 `schemas/pipeline.schema.json`。

| 区块 | 字段 | 含义 |
|------|------|------|
| 核心价值 | `intent` | 解决什么问题 |
| **山底** | `steps[]` | 快速上手：可跟做的 1-2-3 |
| **山顶** | `summit` | 深度体悟：练过才写得清（可空） |
| **踩坑** | `practice[]` | 实践记录：`date` + `note` |
| 适用/边界 | `when_to_use` / `boundaries` | 何时用、何时别硬套 |
| 状态 | `status` | `seed` / `draft` / `validated` / `snowball` |

`seed` = 主题已记下、骨架待实践填充；不等于已经会做。易学错觉警示见 `content/principles.md`。

## 快速开始

```bash
# 校验 + 渲染静态站
python3 scripts/render-site.py

# 本地预览
python3 -m http.server 8777 --directory docs
# 打开 http://localhost:8777
```

新增一条经验：在 `content/pipelines/` 加 YAML → 再跑一遍 `render-site.py`。

## GitHub Pages

- 仓库：https://github.com/czh55/my_pipeline
- 站点：https://czh55.github.io/my_pipeline/（Settings → Pages：`main` / `/docs`）
- 自定义域（若已绑定）：http://chenzhiheng.cn/my_pipeline/

## 滚雪球约定

1. **先有经历，再写章程**——`seed` 可以占位，但升级依赖实践。
2. **步骤要能照做**——别人（或未来的自己）按 steps 走能复现结果。
3. **标明边界**——什么时候不该硬套这条 pipeline。
4. **警惕易学错觉**——看懂 ≠ 会做；深度来自动手次数。
5. **status 只升不降幻想**——用过几次再从 `draft` 升到 `validated`；反复复用、能教人时再标 `snowball`。
