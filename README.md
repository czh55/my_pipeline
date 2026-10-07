# my_pipeline

把经历沉淀成可复制的步骤章程。

## 底层原则

「如何把大象放进冰箱？开门、放入、关门。」

这句话表面是笑话，背后是人类社会共用的底层原则：**解决问题、做事，都有步骤和章程。**

做饭、沟通、学习、拍摄；汇报、任务；以及尚未亲历的事——都适用同一套原则。本仓库只做一件事：把你自己的生活经验，写成可贴合自身的 pipeline，像滚雪球一样把能力滚大。

## 项目结构

```
my_pipeline/
├── content/                 # 真相源（手写 / 随经验追加）
│   ├── principles.md        # 底层原则说明
│   └── pipelines/           # 每条 pipeline 一个 YAML
├── schemas/
│   └── pipeline.schema.json
├── scripts/
│   └── render-site.py       # content → docs 静态站
└── docs/                    # GitHub Pages 根目录
```

## 一条 pipeline 长什么样

见 `schemas/pipeline.schema.json`。最小字段：

| 字段 | 含义 |
|------|------|
| `id` | 唯一标识 |
| `title` | 标题 |
| `domain` | `life` / `work` / `learn` / `create` / `communicate` / `meta` |
| `intent` | 这条章程解决什么 |
| `steps[]` | 有序步骤（name + detail） |
| `status` | `seed` / `draft` / `validated` / `snowball` |

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

1. **先有经历，再写章程**——不凭空发明空壳流程。
2. **步骤要能照做**——别人（或未来的自己）按 steps 走能复现结果。
3. **标明边界**——什么时候不该硬套这条 pipeline。
4. **status 只升不降幻想**——用过几次再从 `draft` 升到 `validated`；反复复用、能教人时再标 `snowball`。
