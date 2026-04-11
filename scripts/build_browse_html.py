#!/usr/bin/env python3
"""
Generate a single static HTML browser at graphs/browse.html for the current
source/ and graphs/ trees.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
OUTPUT_FILE = REPO_ROOT / "graphs" / "browse.html"
ROOT_NAMES = ("source", "graphs")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
TEXT_SUFFIXES = {".json", ".txt", ".md"}


def tree_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def browse_href(path: Path) -> str:
    return os.path.relpath(path, OUTPUT_FILE.parent).replace(os.sep, "/")


def file_sort_key(path: Path) -> tuple[int, str]:
    priority = {
        "index.html": 0,
        "index.htm": 0,
        "metadata.json": 1,
    }
    return (priority.get(path.name, 2), path.name.lower())


def build_item(path: Path) -> dict:
    suffix = path.suffix.lower()
    item = {
        "name": path.name,
        "path": tree_path(path),
        "href": browse_href(path),
        "kind": "file",
    }
    if suffix in IMAGE_SUFFIXES:
        item["kind"] = "image"
    elif suffix in {".html", ".htm"}:
        item["kind"] = "html"
    elif suffix in TEXT_SUFFIXES:
        item["kind"] = "text"
        item["content"] = path.read_text(encoding="utf-8", errors="replace")
    return item


def build_tree(path: Path) -> dict:
    children = sorted([child for child in path.iterdir() if child.is_dir()], key=lambda p: p.name.lower())
    node = {
        "name": path.name,
        "path": tree_path(path),
    }
    if not children:
        items = [build_item(file_path) for file_path in sorted(path.iterdir(), key=file_sort_key) if file_path.is_file()]
        node["leaf"] = True
        node["items"] = items
        node["item_count"] = len(items)
        node["leaf_count"] = 1
        return node

    built_children = [build_tree(child) for child in children]
    node["leaf"] = False
    node["children"] = built_children
    node["leaf_count"] = sum(child["leaf_count"] for child in built_children)
    return node


def build_data() -> dict:
    roots = []
    for name in ROOT_NAMES:
        root_path = REPO_ROOT / name
        if root_path.exists():
            roots.append(build_tree(root_path))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roots": roots,
    }


def render_html(data: dict) -> str:
    payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>a16z Chart Library Browser</title>
  <style>
    :root {{
      --bg: #f4f1e8;
      --panel: #fffaf0;
      --panel-2: #f0ead8;
      --line: #d2c7ac;
      --text: #1d1a14;
      --muted: #726754;
      --accent: #8a3b12;
      --accent-soft: #f3d6bf;
      --shadow: 0 18px 60px rgba(70, 53, 31, 0.12);
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Palatino, serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(138, 59, 18, 0.08), transparent 28%),
        linear-gradient(180deg, #faf6ec 0%, var(--bg) 100%);
      min-height: 100vh;
    }}
    .shell {{
      display: grid;
      grid-template-columns: 360px minmax(0, 1fr);
      min-height: 100vh;
    }}
    .sidebar {{
      border-right: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(255, 250, 240, 0.95), rgba(240, 234, 216, 0.96));
      padding: 20px 18px 32px;
      overflow: auto;
    }}
    .content {{
      padding: 24px;
      overflow: auto;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
      line-height: 1.05;
      letter-spacing: -0.03em;
    }}
    .subhead {{
      margin: 0 0 18px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.45;
    }}
    .tree {{
      display: grid;
      gap: 10px;
    }}
    details {{
      border-left: 1px solid var(--line);
      padding-left: 12px;
      margin-left: 4px;
    }}
    details.root {{
      border-left: none;
      padding-left: 0;
      margin-left: 0;
    }}
    summary {{
      cursor: pointer;
      list-style: none;
      font-weight: 600;
      padding: 4px 0;
    }}
    summary::-webkit-details-marker {{
      display: none;
    }}
    summary::before {{
      content: "▸";
      display: inline-block;
      width: 1em;
      color: var(--accent);
      transition: transform 120ms ease;
    }}
    details[open] > summary::before {{
      transform: rotate(90deg);
    }}
    .branch-label {{
      display: inline-flex;
      align-items: baseline;
      gap: 8px;
    }}
    .count {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 500;
      letter-spacing: 0.02em;
    }}
    .leaf-button {{
      width: 100%;
      margin: 5px 0;
      border: 1px solid transparent;
      border-radius: 12px;
      background: transparent;
      color: inherit;
      text-align: left;
      padding: 9px 12px;
      cursor: pointer;
      font: inherit;
      transition: background 120ms ease, border-color 120ms ease, transform 120ms ease;
    }}
    .leaf-button:hover {{
      background: rgba(138, 59, 18, 0.08);
      border-color: rgba(138, 59, 18, 0.18);
    }}
    .leaf-button.active {{
      background: var(--accent-soft);
      border-color: rgba(138, 59, 18, 0.28);
      transform: translateX(2px);
    }}
    .leaf-path {{
      display: block;
      font-size: 12px;
      color: var(--muted);
      margin-top: 2px;
      word-break: break-word;
    }}
    .panel {{
      background: rgba(255, 250, 240, 0.92);
      border: 1px solid rgba(210, 199, 172, 0.9);
      border-radius: 24px;
      box-shadow: var(--shadow);
      overflow: hidden;
    }}
    .panel-header {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: end;
      padding: 20px 24px 16px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(255, 247, 235, 0.98), rgba(247, 240, 225, 0.98));
    }}
    .eyebrow {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 6px;
    }}
    .title {{
      margin: 0;
      font-size: 24px;
      line-height: 1.15;
      word-break: break-word;
    }}
    .meta {{
      color: var(--muted);
      font-size: 13px;
      text-align: right;
      white-space: nowrap;
    }}
    .controls {{
      display: flex;
      gap: 10px;
      align-items: center;
      padding: 14px 24px;
      border-bottom: 1px solid var(--line);
      background: rgba(255, 250, 240, 0.82);
      flex-wrap: wrap;
    }}
    .button {{
      border: 1px solid var(--line);
      border-radius: 999px;
      background: white;
      color: var(--text);
      padding: 8px 14px;
      cursor: pointer;
      font: inherit;
    }}
    .button:hover {{
      border-color: var(--accent);
      color: var(--accent);
    }}
    .button:disabled {{
      opacity: 0.4;
      cursor: default;
      color: var(--muted);
      border-color: var(--line);
    }}
    .hint {{
      color: var(--muted);
      font-size: 13px;
      margin-left: auto;
    }}
    .item-strip {{
      display: flex;
      gap: 8px;
      padding: 16px 24px 0;
      overflow: auto;
      scrollbar-width: thin;
    }}
    .item-chip {{
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.75);
      padding: 7px 12px;
      cursor: pointer;
      white-space: nowrap;
      font: inherit;
      font-size: 13px;
    }}
    .item-chip.active {{
      background: var(--accent);
      color: white;
      border-color: var(--accent);
    }}
    .viewer {{
      padding: 20px 24px 24px;
    }}
    .viewer-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: baseline;
      margin-bottom: 14px;
      flex-wrap: wrap;
    }}
    .viewer-path {{
      font-size: 15px;
      font-weight: 600;
      word-break: break-word;
    }}
    .viewer-link a {{
      color: var(--accent);
      text-decoration: none;
      font-size: 13px;
    }}
    .viewer-link a:hover {{
      text-decoration: underline;
    }}
    .stage {{
      background: rgba(243, 236, 222, 0.65);
      border: 1px solid var(--line);
      border-radius: 20px;
      min-height: 68vh;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .stage iframe,
    .stage pre,
    .stage .placeholder {{
      width: 100%;
      min-height: 68vh;
      align-self: stretch;
    }}
    .stage img {{
      width: auto;
      height: auto;
      min-height: 0;
      max-width: 100%;
      max-height: 600px;
      display: block;
      align-self: center;
      background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(244,241,232,0.9));
    }}
    .stage iframe {{
      border: 0;
      background: white;
    }}
    .stage pre {{
      margin: 0;
      padding: 20px;
      overflow: auto;
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 13px;
      line-height: 1.5;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .placeholder {{
      display: grid;
      place-items: center;
      color: var(--muted);
      padding: 24px;
      text-align: center;
    }}
    @media (max-width: 980px) {{
      .shell {{
        grid-template-columns: 1fr;
      }}
      .sidebar {{
        max-height: 42vh;
        border-right: none;
        border-bottom: 1px solid var(--line);
      }}
      .content {{
        padding: 18px;
      }}
      .panel-header {{
        padding: 18px;
      }}
      .controls,
      .item-strip,
      .viewer {{
        padding-left: 18px;
        padding-right: 18px;
      }}
      .hint {{
        width: 100%;
        margin-left: 0;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <aside class="sidebar">
      <h1>a16z Library Browser</h1>
      <p class="subhead">
        Directory tree on the left, leaf-folder gallery on the right.
        Use <strong>Left</strong>/<strong>Right</strong> for items and
        <strong>Up</strong>/<strong>Down</strong> for sibling leaf folders.
      </p>
      <div id="tree" class="tree"></div>
    </aside>
    <main class="content">
      <section class="panel">
        <div class="panel-header">
          <div>
            <div class="eyebrow">Static Browser</div>
            <h2 id="panel-title" class="title">Choose a leaf directory</h2>
          </div>
          <div id="panel-meta" class="meta">Generated {data["generated_at"]}</div>
        </div>
        <div class="controls">
          <button id="prev-dir" class="button">Previous Directory</button>
          <button id="prev-item" class="button">Previous Item</button>
          <button id="next-item" class="button">Next Item</button>
          <button id="next-dir" class="button">Next Directory</button>
          <div id="dir-status" class="hint"></div>
        </div>
        <div id="item-strip" class="item-strip"></div>
        <div class="viewer">
          <div class="viewer-head">
            <div id="viewer-path" class="viewer-path"></div>
            <div id="viewer-link" class="viewer-link"></div>
          </div>
          <div id="stage" class="stage">
            <div class="placeholder">Select a leaf directory to browse its files.</div>
          </div>
        </div>
      </section>
    </main>
  </div>

  <script id="tree-data" type="application/json">{payload}</script>
  <script>
    const data = JSON.parse(document.getElementById("tree-data").textContent);
    const treeEl = document.getElementById("tree");
    const itemStripEl = document.getElementById("item-strip");
    const panelTitleEl = document.getElementById("panel-title");
    const panelMetaEl = document.getElementById("panel-meta");
    const dirStatusEl = document.getElementById("dir-status");
    const viewerPathEl = document.getElementById("viewer-path");
    const viewerLinkEl = document.getElementById("viewer-link");
    const stageEl = document.getElementById("stage");
    const prevDirEl = document.getElementById("prev-dir");
    const nextDirEl = document.getElementById("next-dir");
    const prevItemEl = document.getElementById("prev-item");
    const nextItemEl = document.getElementById("next-item");

    const leafOrder = [];
    const leafMap = new Map();
    const leafButtons = new Map();
    let currentLeafPath = null;
    let currentItemIndex = 0;

    function displayCountLabel(label, count, noun) {{
      return `${{label}} (${{count}} ${{noun}}${{count === 1 ? "" : "s"}})`;
    }}

    function openAncestors(element) {{
      let parent = element.parentElement;
      while (parent) {{
        if (parent.tagName === "DETAILS") {{
          parent.open = true;
        }}
        parent = parent.parentElement;
      }}
    }}

    function renderTreeNode(node, parentEl, depth) {{
      if (node.leaf) {{
        leafOrder.push(node.path);
        leafMap.set(node.path, node);

        const button = document.createElement("button");
        button.className = "leaf-button";
        button.dataset.path = node.path;
        button.innerHTML = `
          <strong>${{node.name}}</strong>
          <span class="leaf-path">${{node.path}}</span>
          <span class="count">${{node.item_count}} file${{node.item_count === 1 ? "" : "s"}}</span>
        `;
        button.addEventListener("click", () => selectLeaf(node.path));
        leafButtons.set(node.path, button);
        parentEl.appendChild(button);
        return;
      }}

      const details = document.createElement("details");
      details.className = depth === 0 ? "root" : "";
      details.open = depth === 0 || node.name === "graphs";

      const summary = document.createElement("summary");
      summary.innerHTML = `
        <span class="branch-label">
          <span>${{node.name}}</span>
          <span class="count">${{node.leaf_count}} leaf${{node.leaf_count === 1 ? "" : "s"}}</span>
        </span>
      `;
      details.appendChild(summary);

      const container = document.createElement("div");
      node.children.forEach((child) => renderTreeNode(child, container, depth + 1));
      details.appendChild(container);
      parentEl.appendChild(details);
    }}

    function renderTree() {{
      data.roots.forEach((root) => renderTreeNode(root, treeEl, 0));
    }}

    function getCurrentLeaf() {{
      return currentLeafPath ? leafMap.get(currentLeafPath) : null;
    }}

    function setActiveButton(path) {{
      leafButtons.forEach((button, candidate) => {{
        button.classList.toggle("active", candidate === path);
      }});
      const button = leafButtons.get(path);
      if (button) {{
        openAncestors(button);
        button.scrollIntoView({{block: "nearest"}});
      }}
    }}

    function renderStage(item) {{
      stageEl.textContent = "";
      if (!item) {{
        const empty = document.createElement("div");
        empty.className = "placeholder";
        empty.textContent = "This directory has no files to preview.";
        stageEl.appendChild(empty);
        return;
      }}

      if (item.kind === "image") {{
        const img = document.createElement("img");
        img.src = item.href;
        img.alt = item.name;
        stageEl.appendChild(img);
        return;
      }}

      if (item.kind === "html") {{
        const iframe = document.createElement("iframe");
        iframe.src = item.href;
        iframe.loading = "lazy";
        stageEl.appendChild(iframe);
        return;
      }}

      if (item.kind === "text") {{
        const pre = document.createElement("pre");
        pre.textContent = item.content || "";
        stageEl.appendChild(pre);
        return;
      }}

      const placeholder = document.createElement("div");
      placeholder.className = "placeholder";
      placeholder.innerHTML = `No inline preview for <strong>${{item.name}}</strong>.`;
      stageEl.appendChild(placeholder);
    }}

    function renderItems(leaf) {{
      itemStripEl.textContent = "";
      leaf.items.forEach((item, index) => {{
        const chip = document.createElement("button");
        chip.className = "item-chip";
        chip.textContent = item.name;
        chip.classList.toggle("active", index === currentItemIndex);
        chip.addEventListener("click", () => {{
          currentItemIndex = index;
          renderViewer();
        }});
        itemStripEl.appendChild(chip);
      }});
    }}

    function renderViewer() {{
      const leaf = getCurrentLeaf();
      if (!leaf) {{
        panelTitleEl.textContent = "Choose a leaf directory";
        panelMetaEl.textContent = `Generated ${{data.generated_at}}`;
        dirStatusEl.textContent = "";
        viewerPathEl.textContent = "";
        viewerLinkEl.textContent = "";
        itemStripEl.textContent = "";
        renderStage(null);
        prevDirEl.disabled = true;
        nextDirEl.disabled = true;
        prevItemEl.disabled = true;
        nextItemEl.disabled = true;
        return;
      }}

      if (currentItemIndex >= leaf.items.length) {{
        currentItemIndex = Math.max(leaf.items.length - 1, 0);
      }}
      if (currentItemIndex < 0) {{
        currentItemIndex = 0;
      }}

      const leafIndex = leafOrder.indexOf(leaf.path);
      const item = leaf.items[currentItemIndex] || null;

      panelTitleEl.textContent = leaf.path;
      panelMetaEl.textContent = displayCountLabel("Leaf directory", leaf.item_count, "file");
      dirStatusEl.textContent = `Directory ${{leafIndex + 1}} of ${{leafOrder.length}}`;
      viewerPathEl.textContent = item
        ? `${{item.path}} · item ${{currentItemIndex + 1}} of ${{Math.max(leaf.items.length, 1)}}`
        : "No previewable files";
      viewerLinkEl.innerHTML = item
        ? `<a href="${{item.href}}" target="_blank" rel="noopener">Open ${{item.name}}</a>`
        : "";

      prevDirEl.disabled = leafIndex <= 0;
      nextDirEl.disabled = leafIndex === -1 || leafIndex >= leafOrder.length - 1;
      prevItemEl.disabled = currentItemIndex <= 0;
      nextItemEl.disabled = leaf.items.length === 0 || currentItemIndex >= leaf.items.length - 1;

      renderItems(leaf);
      renderStage(item);
    }}

    function selectLeaf(path) {{
      if (!leafMap.has(path)) {{
        return;
      }}
      currentLeafPath = path;
      currentItemIndex = 0;
      setActiveButton(path);
      renderViewer();
    }}

    function moveDirectory(offset) {{
      const leaf = getCurrentLeaf();
      if (!leaf) {{
        if (leafOrder.length) {{
          selectLeaf(leafOrder[0]);
        }}
        return;
      }}
      const currentIndex = leafOrder.indexOf(leaf.path);
      const nextIndex = currentIndex + offset;
      if (nextIndex >= 0 && nextIndex < leafOrder.length) {{
        selectLeaf(leafOrder[nextIndex]);
      }}
    }}

    function moveItem(offset) {{
      const leaf = getCurrentLeaf();
      if (!leaf || !leaf.items.length) {{
        return;
      }}
      const nextIndex = currentItemIndex + offset;
      if (nextIndex >= 0 && nextIndex < leaf.items.length) {{
        currentItemIndex = nextIndex;
        renderViewer();
      }}
    }}

    prevDirEl.addEventListener("click", () => moveDirectory(-1));
    nextDirEl.addEventListener("click", () => moveDirectory(1));
    prevItemEl.addEventListener("click", () => moveItem(-1));
    nextItemEl.addEventListener("click", () => moveItem(1));

    window.addEventListener("keydown", (event) => {{
      const tag = document.activeElement && document.activeElement.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") {{
        return;
      }}
      if (event.key === "ArrowLeft") {{
        event.preventDefault();
        moveItem(-1);
      }} else if (event.key === "ArrowRight") {{
        event.preventDefault();
        moveItem(1);
      }} else if (event.key === "ArrowUp") {{
        event.preventDefault();
        moveDirectory(-1);
      }} else if (event.key === "ArrowDown") {{
        event.preventDefault();
        moveDirectory(1);
      }}
    }});

    renderTree();
    if (leafOrder.length) {{
      selectLeaf(leafOrder[0]);
    }} else {{
      renderViewer();
    }}
  </script>
</body>
</html>
"""


def main() -> None:
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(render_html(build_data()), encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
