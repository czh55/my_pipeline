#!/usr/bin/env python3
"""Validate content/pipelines/*.yaml and render docs/ static site."""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "pipelines"
SCHEMA = ROOT / "schemas" / "pipeline.schema.json"
DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"
PIPE_DIR = DOCS / "pipelines"

DOMAIN_LABEL = {
    "meta": "元原则",
    "life": "生活",
    "work": "工作",
    "learn": "学习",
    "create": "创作",
    "communicate": "沟通",
}

STATUS_LABEL = {
    "seed": "种子",
    "draft": "草稿",
    "validated": "已验证",
    "snowball": "滚雪球",
}

ORIGIN_LABEL = {
    "self": "自己定义",
    "borrowed": "拿来主义",
}

REQUIRED = ("id", "title", "domain", "intent", "steps", "status")


def load_pipelines() -> list[dict]:
    files = sorted(CONTENT.glob("*.yaml")) + sorted(CONTENT.glob("*.yml"))
    if not files:
        print("error: no pipelines under content/pipelines/", file=sys.stderr)
        sys.exit(1)

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    domains = set(schema["properties"]["domain"]["enum"])
    statuses = set(schema["properties"]["status"]["enum"])
    origins = set(schema["properties"]["origin"]["enum"])

    pipelines: list[dict] = []
    seen: set[str] = set()
    for path in files:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            fail(path, "root must be a mapping")
        for key in REQUIRED:
            if key not in data:
                fail(path, f"missing required field: {key}")
        if data["id"] in seen:
            fail(path, f"duplicate id: {data['id']}")
        seen.add(data["id"])
        if data["domain"] not in domains:
            fail(path, f"invalid domain: {data['domain']}")
        if data["status"] not in statuses:
            fail(path, f"invalid status: {data['status']}")
        origin = data.get("origin") or "self"
        if origin not in origins:
            fail(path, f"invalid origin: {origin}")
        data["origin"] = origin
        if origin == "borrowed" and not (data.get("source") or "").strip():
            fail(path, "borrowed pipeline needs source (出处)")
        steps = data["steps"]
        if not isinstance(steps, list) or len(steps) < 2:
            fail(path, "steps must be a list with at least 2 items")
        for i, step in enumerate(steps):
            if not isinstance(step, dict) or "name" not in step or "detail" not in step:
                fail(path, f"steps[{i}] needs name + detail")
        pipelines.append(data)

    order = {"snowball": 0, "validated": 1, "draft": 2, "seed": 3}
    pipelines.sort(key=lambda p: (order.get(p["status"], 9), p["domain"], p["id"]))
    return pipelines


def fail(path: Path, msg: str) -> None:
    print(f"error: {path.name}: {msg}", file=sys.stderr)
    sys.exit(1)


def esc(text: str | None) -> str:
    return html.escape(text or "", quote=True)


def nav(active: str, depth: int = 0) -> str:
    prefix = "../" * depth
    items = [
        (f"{prefix}index.html", "首页", "home"),
        (f"{prefix}principles.html", "原则", "principles"),
        (f"{prefix}pipelines/index.html", "全部章程", "pipelines"),
    ]
    links = []
    for href, label, key in items:
        cls = ' class="active"' if key == active else ""
        links.append(f'<a{cls} href="{href}">{label}</a>')
    return (
        '<nav class="top">'
        f'<a class="brand" href="{prefix}index.html">my_pipeline</a>'
        + "".join(links)
        + "</nav>"
    )


def page(title: str, active: str, body: str, depth: int = 0) -> str:
    prefix = "../" * depth
    nav_html = nav(active, depth)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · my_pipeline</title>
<link rel="stylesheet" href="{prefix}assets/site.css">
</head>
<body>
<div class="wrap">
{nav_html}
{body}
<footer>经历 → 章程 → 复用 · 山底上路，山顶沉淀 · 中间必须亲自练</footer>
</div>
</body>
</html>
"""


def render_index(pipelines: list[dict]) -> str:
    domains = {}
    for p in pipelines:
        domains.setdefault(p["domain"], []).append(p)

    cards = []
    for domain, items in domains.items():
        label = DOMAIN_LABEL.get(domain, domain)
        cards.append(
            f'<a class="card" href="pipelines/index.html#{esc(domain)}">'
            f'<div class="kicker">{esc(domain)}</div>'
            f"<h2>{esc(label)}</h2>"
            f"<p>{len(items)} 条章程</p></a>"
        )

    featured = pipelines[:6]
    feat_html = []
    for p in featured:
        feat_html.append(
            f'<a class="pipe-row" href="pipelines/{esc(p["id"])}.html">'
            f'<span class="num">{esc(DOMAIN_LABEL.get(p["domain"], p["domain"]))}</span>'
            f"<div><strong>{esc(p['title'])}</strong>"
            f'<p class="muted">{esc(p["intent"])}</p></div>'
            f'<span class="tag origin o-{esc(p.get("origin") or "self")}">{esc(ORIGIN_LABEL.get(p.get("origin") or "self", "自己定义"))}</span>'
            f'<span class="status s-{esc(p["status"])}">{esc(STATUS_LABEL[p["status"]])}</span>'
            f"</a>"
        )

    body = f"""
<header class="hero">
  <p class="eyebrow">经验章程库</p>
  <h1>my_pipeline</h1>
  <p class="north-star">我有信心能够处理好生活中的各种事情。</p>
  <p>把大象放进冰箱：开门、放入、关门。背后是人生与工作共用的底层原则——做事都有步骤和章程。不开心遇到新问题，就总结（或并入）一条新 pipeline。</p>
</header>

<section class="metaphor">
  <ol class="steps big">
    <li><span class="n">1</span><div><strong>开门</strong><p>创造入口</p></div></li>
    <li><span class="n">2</span><div><strong>放入</strong><p>执行改变</p></div></li>
    <li><span class="n">3</span><div><strong>关门</strong><p>收束确认</p></div></li>
  </ol>
</section>

<section class="warning">
  <h2 class="section-title">核心警示</h2>
  <p>Pipeline 说起来往往简单几步，像菜谱一样「一看就会」——但菜谱一直存在，饭的味道却千差万别。你对一条章程的感受有多深，取决于你有多少次真实动手实践。</p>
  <p class="warn-lead">它最大的价值在<strong>山底</strong>（快速上手）与<strong>山顶</strong>（个人总结）；不能抄近路从山底瞬移到山顶。中间必须亲自练。</p>
  <p class="more"><a href="principles.html">读完整原则 →</a></p>
</section>

<section>
  <h2 class="section-title">按领域</h2>
  <div class="grid">{"".join(cards)}</div>
</section>

<section>
  <h2 class="section-title">章程入口</h2>
  <div class="pipe-list">{"".join(feat_html)}</div>
  <p class="more"><a href="pipelines/index.html">查看全部 →</a></p>
</section>
"""
    return page("首页", "home", body)


def render_principles() -> str:
    md = (ROOT / "content" / "principles.md").read_text(encoding="utf-8")
    # Minimal markdown → HTML for this short doc (headings + lists + quotes + paragraphs)
    lines = md.splitlines()
    out: list[str] = []
    in_list = False
    for line in lines:
        if line.startswith("# "):
            if in_list:
                out.append("</ul>")
                in_list = False
            continue  # page title already set
        if line.startswith("### "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h3>{esc(line[4:])}</h3>")
        elif line.startswith("## "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h2>{esc(line[3:])}</h2>")
        elif line.startswith("|") and "---" not in line:
            if in_list:
                out.append("</ul>")
                in_list = False
            # skip table rendering complexity — simple pre for domain table block handled below
            out.append(f"<p class=\"table-line\">{esc(line)}</p>")
        elif line.startswith("> "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f'<blockquote>{esc(line[2:])}</blockquote>')
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{esc(line[2:])}</li>")
        elif line.startswith(("1. ", "2. ", "3. ", "4. ")):
            if in_list:
                out.append("</ul>")
                in_list = False
            # collect numbered as ol later — simple p for now
            out.append(f"<p class=\"ol-item\">{esc(line)}</p>")
        elif line.strip() == "":
            if in_list:
                out.append("</ul>")
                in_list = False
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<p>{esc(line)}</p>")
    if in_list:
        out.append("</ul>")

    body = f"""
<header class="hero">
  <p class="eyebrow">底层原则</p>
  <h1>步骤与章程</h1>
  <p>先有步骤，再谈熟练。另请牢记：看懂 pipeline ≠ 会做；山底与山顶有价值，中间必须亲自练。</p>
</header>
<article class="prose">
{"".join(out)}
</article>
"""
    return page("原则", "principles", body)


def render_pipeline_list(pipelines: list[dict]) -> str:
    by_domain: dict[str, list[dict]] = {}
    for p in pipelines:
        by_domain.setdefault(p["domain"], []).append(p)

    sections = []
    for domain, items in by_domain.items():
        rows = []
        for p in items:
            rows.append(
                f'<a class="pipe-row" href="{esc(p["id"])}.html">'
                f'<span class="num">{len(p["steps"])} 步</span>'
                f"<div><strong>{esc(p['title'])}</strong>"
                f'<p class="muted">{esc(p["intent"])}</p></div>'
                f'<span class="tag origin o-{esc(p.get("origin") or "self")}">{esc(ORIGIN_LABEL.get(p.get("origin") or "self", "自己定义"))}</span>'
                f'<span class="status s-{esc(p["status"])}">{esc(STATUS_LABEL[p["status"]])}</span>'
                f"</a>"
            )
        sections.append(
            f'<section id="{esc(domain)}">'
            f'<h2 class="section-title">{esc(DOMAIN_LABEL.get(domain, domain))}'
            f' <span class="count">{len(items)}</span></h2>'
            f'<div class="pipe-list">{"".join(rows)}</div></section>'
        )

    body = f"""
<header class="hero">
  <p class="eyebrow">全部章程</p>
  <h1>Pipelines</h1>
  <p>共 {len(pipelines)} 条。随生活经验追加 YAML，再渲染即可上线。</p>
</header>
{"".join(sections)}
"""
    return page("全部章程", "pipelines", body, depth=1)


def render_pipeline_detail(p: dict) -> str:
    steps = []
    for i, step in enumerate(p["steps"], 1):
        steps.append(
            f"<li><span class=\"n\">{i}</span>"
            f"<div><strong>{esc(step['name'])}</strong>"
            f"<p>{esc(step['detail'])}</p></div></li>"
        )

    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in p.get("tags") or [])
    origin = p.get("origin") or "self"
    meta_bits = [
        f'<span class="status s-{esc(p["status"])}">{esc(STATUS_LABEL[p["status"]])}</span>',
        f'<span class="tag domain">{esc(DOMAIN_LABEL.get(p["domain"], p["domain"]))}</span>',
        f'<span class="tag origin o-{esc(origin)}">{esc(ORIGIN_LABEL.get(origin, origin))}</span>',
    ]
    if p.get("updated"):
        meta_bits.append(f'<span class="muted">{esc(p["updated"])}</span>')

    summit = (p.get("summit") or "").strip()
    summit_html = (
        f"<p>{esc(summit)}</p>"
        if summit
        else '<p class="muted">待实践填充——山顶体悟只在练过之后写，不在看懂步骤时编。</p>'
    )

    practice_items = p.get("practice") or []
    if practice_items:
        practice_html = "<ul>" + "".join(
            f"<li><strong>{esc(item.get('date', ''))}</strong> — {esc(item.get('note', ''))}</li>"
            for item in practice_items
        ) + "</ul>"
    else:
        practice_html = '<p class="muted">尚无踩坑记录。每练一轮，在 YAML 的 practice 里追加一行 date + note。</p>'

    extras = []
    if p.get("principle"):
        extras.append(f"<h2>心法</h2><p class=\"principle\">{esc(p['principle'])}</p>")
    if p.get("when_to_use"):
        extras.append(f"<h2>何时使用</h2><p>{esc(p['when_to_use'])}</p>")
    if p.get("boundaries"):
        extras.append(f"<h2>边界</h2><p>{esc(p['boundaries'])}</p>")
    extras.append(
        f"<h2>来源类型</h2><p>{esc(ORIGIN_LABEL.get(origin, origin))}"
        + ("（须注明出处）" if origin == "borrowed" else "")
        + "</p>"
    )
    if p.get("source"):
        extras.append(f"<h2>来源 / 参考</h2><p>{esc(p['source'])}</p>")

    body = f"""
<header class="hero">
  <p class="eyebrow">{esc(p["id"])}</p>
  <h1>{esc(p["title"])}</h1>
  <p>{esc(p["intent"])}</p>
  <div class="meta-row">{"".join(meta_bits)}{tags}</div>
</header>
<section class="warning compact">
  <p class="warn-lead">易学错觉：看懂步骤 ≠ 会做。价值在山底上路与山顶总结；中间必须亲自练。
  <a href="../principles.html">原则全文</a></p>
</section>
<section>
  <h2 class="section-title">山底 · 快速上手</h2>
  <ol class="steps">{"".join(steps)}</ol>
</section>
<section class="prose stage">
  <h2 class="section-title">山顶 · 深度体悟</h2>
  {summit_html}
</section>
<section class="prose stage">
  <h2 class="section-title">实践踩坑</h2>
  {practice_html}
</section>
<article class="prose extras">
{"".join(extras)}
</article>
<p class="more"><a href="index.html">← 全部章程</a></p>
"""
    return page(p["title"], "pipelines", body, depth=1)


def write_css() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "site.css").write_text(
        """
:root {
  --bg: #14110e;
  --surface: rgba(255,244,230,0.04);
  --border: rgba(255,220,180,0.12);
  --text: #f4ebe1;
  --muted: #a89888;
  --accent: #e8a05c;
  --accent2: #8fb9a8;
  --ink: #2a221c;
  --font-display: "DIN Condensed", "Avenir Next Condensed", "PingFang SC", "Helvetica Neue", sans-serif;
  --font-body: "IBM Plex Sans", "Avenir Next", "PingFang SC", "Helvetica Neue", sans-serif;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: var(--font-body);
  background:
    radial-gradient(800px 420px at 8% -8%, rgba(232,160,92,0.16), transparent 55%),
    radial-gradient(640px 380px at 100% 0%, rgba(143,185,168,0.10), transparent 50%),
    linear-gradient(180deg, #1a1612 0%, var(--bg) 40%);
  color: var(--text);
  min-height: 100vh;
  line-height: 1.65;
}
a { color: var(--accent2); text-decoration: none; }
a:hover { text-decoration: underline; }
.wrap { max-width: 880px; margin: 0 auto; padding: 28px 20px 72px; }
nav.top {
  display: flex; flex-wrap: wrap; gap: 10px 18px; align-items: center;
  padding: 10px 0 22px; border-bottom: 1px solid var(--border); margin-bottom: 32px;
}
nav.top .brand {
  font-family: var(--font-display);
  font-size: 1.2rem; font-weight: 700; letter-spacing: 0.04em;
  color: var(--text); margin-right: auto; text-transform: lowercase;
}
nav.top a { color: var(--muted); font-size: 0.9rem; }
nav.top a.active { color: var(--accent); }
.hero { margin-bottom: 36px; }
.hero .eyebrow {
  font-size: 0.75rem; letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--accent); font-weight: 700; margin-bottom: 10px;
}
.hero h1 {
  font-family: var(--font-display);
  font-size: clamp(2rem, 5vw, 2.9rem);
  letter-spacing: -0.02em; line-height: 1.1; margin-bottom: 14px;
}
.hero p { color: var(--muted); max-width: 40rem; }
.hero p.north-star {
  color: var(--text); font-family: var(--font-display); font-size: 1.15rem;
  margin: 0 0 12px; max-width: 36rem;
}
.meta-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 16px; }
.section-title {
  font-family: var(--font-display);
  font-size: 1.35rem; margin: 8px 0 14px; letter-spacing: 0.02em;
}
.section-title .count {
  font-size: 0.85rem; color: var(--muted); font-weight: 500; margin-left: 6px;
}
.grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 36px;
}
@media (max-width: 720px) { .grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 420px) { .grid { grid-template-columns: 1fr; } }
.card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; padding: 16px; display: block; color: inherit;
}
a.card:hover { border-color: rgba(232,160,92,0.5); text-decoration: none; transform: translateY(-1px); }
.card .kicker {
  font-size: 0.7rem; letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--accent); font-weight: 700;
}
.card h2 { font-family: var(--font-display); font-size: 1.15rem; margin: 8px 0 4px; }
.card p { color: var(--muted); font-size: 0.88rem; }
.metaphor {
  background: linear-gradient(135deg, rgba(232,160,92,0.12), rgba(143,185,168,0.08));
  border: 1px solid var(--border); border-radius: 16px; padding: 22px 18px; margin-bottom: 36px;
}
.warning {
  background: rgba(232,160,92,0.08);
  border: 1px solid rgba(232,160,92,0.35);
  border-radius: 16px; padding: 22px 18px; margin-bottom: 36px;
}
.warning p { color: var(--muted); margin-bottom: 10px; }
.warning .warn-lead { color: var(--text); font-family: var(--font-display); font-size: 1.05rem; line-height: 1.5; }
.warning.compact { padding: 14px 16px; margin-bottom: 28px; }
.warning.compact .warn-lead { font-size: 0.95rem; margin: 0; }
.warning strong { color: var(--accent); }
.stage { margin: 28px 0; padding-top: 8px; border-top: 1px solid var(--border); }
.steps { list-style: none; display: flex; flex-direction: column; gap: 14px; }
.steps.big { gap: 16px; }
.steps li {
  display: grid; grid-template-columns: 44px 1fr; gap: 14px; align-items: start;
}
.steps .n {
  width: 44px; height: 44px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display); font-weight: 700; font-size: 1.1rem;
  background: var(--accent); color: var(--ink);
}
.steps.big .n { width: 52px; height: 52px; font-size: 1.25rem; }
.steps strong { font-family: var(--font-display); font-size: 1.1rem; }
.steps p { color: var(--muted); font-size: 0.92rem; margin-top: 2px; }
.pipe-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 28px; }
.pipe-row {
  display: grid; grid-template-columns: 72px 1fr auto; gap: 12px; align-items: center;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; padding: 14px 16px; color: inherit;
}
a.pipe-row:hover { border-color: rgba(232,160,92,0.45); text-decoration: none; }
.pipe-row .num { font-size: 0.78rem; color: var(--accent); font-weight: 700; letter-spacing: 0.04em; }
.pipe-row .muted, .muted { color: var(--muted); font-size: 0.88rem; }
.status {
  font-size: 0.72rem; padding: 3px 9px; border-radius: 999px;
  border: 1px solid var(--border); color: var(--muted); white-space: nowrap;
}
.status.s-seed { color: var(--muted); }
.status.s-draft { color: #c4b08a; border-color: rgba(196,176,138,0.35); }
.status.s-validated { color: var(--accent2); border-color: rgba(143,185,168,0.4); }
.status.s-snowball { color: var(--accent); border-color: rgba(232,160,92,0.45); background: rgba(232,160,92,0.1); }
.tag {
  display: inline-block; font-size: 0.72rem; padding: 2px 8px; border-radius: 999px;
  background: rgba(143,185,168,0.12); color: var(--accent2); margin-right: 4px;
}
.tag.domain { background: rgba(232,160,92,0.12); color: var(--accent); }
.tag.origin.o-self { background: rgba(143,185,168,0.18); color: var(--accent2); }
.tag.origin.o-borrowed { background: rgba(120,150,200,0.18); color: #9bb4d4; }
.prose h2 { font-family: var(--font-display); font-size: 1.25rem; margin: 28px 0 10px; }
.prose h3 { font-family: var(--font-display); font-size: 1.05rem; margin: 18px 0 8px; color: var(--accent); }
.prose p, .prose li { color: var(--muted); margin-bottom: 10px; }
.prose ul { margin: 8px 0 12px 1.2rem; }
.prose blockquote {
  border-left: 3px solid var(--accent); padding: 8px 0 8px 16px;
  color: var(--text); font-family: var(--font-display); font-size: 1.15rem;
  margin: 16px 0;
}
.prose .principle {
  font-family: var(--font-display); font-size: 1.2rem; color: var(--accent); margin-bottom: 16px;
}
.prose .table-line { font-family: ui-monospace, monospace; font-size: 0.85rem; }
.prose .ol-item { margin-left: 0.5rem; }
.more { margin-top: 8px; }
footer {
  margin-top: 48px; padding-top: 18px; border-top: 1px solid var(--border);
  color: var(--muted); font-size: 0.85rem;
}
@media (max-width: 560px) {
  .pipe-row { grid-template-columns: 1fr; }
  .pipe-row .status { justify-self: start; }
}
""".strip()
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    pipelines = load_pipelines()
    DOCS.mkdir(parents=True, exist_ok=True)
    PIPE_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    write_css()

    (DOCS / "index.html").write_text(render_index(pipelines), encoding="utf-8")
    (DOCS / "principles.html").write_text(render_principles(), encoding="utf-8")
    (PIPE_DIR / "index.html").write_text(render_pipeline_list(pipelines), encoding="utf-8")
    for p in pipelines:
        (PIPE_DIR / f"{p['id']}.html").write_text(render_pipeline_detail(p), encoding="utf-8")

    index_json = [
        {
            "id": p["id"],
            "title": p["title"],
            "domain": p["domain"],
            "status": p["status"],
            "origin": p.get("origin") or "self",
            "steps": len(p["steps"]),
        }
        for p in pipelines
    ]
    (DOCS / "index.json").write_text(
        json.dumps(index_json, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"rendered {len(pipelines)} pipelines → {DOCS}")


if __name__ == "__main__":
    main()
