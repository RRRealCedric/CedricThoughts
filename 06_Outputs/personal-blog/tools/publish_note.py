#!/usr/bin/env python3
"""
Publish a Markdown note from the vault into the public blog.

The script intentionally has no third-party dependencies. It converts common
Markdown structures into the existing blog HTML style and can insert a matching
entry into the homepage Writing list.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path


BLOG_ROOT = Path(__file__).resolve().parents[1]
VAULT_ROOT = BLOG_ROOT.parents[1]
NOTES_DIR = BLOG_ROOT / "notes"
INDEX_PATH = BLOG_ROOT / "index.html"

ALLOWED_CATEGORIES = {"project", "philosophy", "learning"}
CATEGORY_LABELS = {
    "project": "Project Note",
    "philosophy": "Philosophy",
    "learning": "Learning",
}


@dataclass
class NoteMetadata:
    title: str
    description: str
    category: str
    label: str
    slug: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a vault Markdown note into a public blog HTML page."
    )
    parser.add_argument("source", help="Markdown file path relative to the vault root.")
    parser.add_argument("--slug", help="Output file name without .html.")
    parser.add_argument("--title", help="Public article title. Defaults to the first H1 or file stem.")
    parser.add_argument("--description", help="One-sentence summary for the homepage and article lede.")
    parser.add_argument(
        "--category",
        default="learning",
        choices=sorted(ALLOWED_CATEGORIES),
        help="Homepage filter category.",
    )
    parser.add_argument("--label", help="Small label above the article title.")
    parser.add_argument(
        "--no-index",
        action="store_true",
        help="Generate the article page without adding it to the homepage Writing list.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the generated HTML page if it already exists.",
    )
    return parser.parse_args()


def resolve_source(source: str) -> Path:
    path = Path(source)
    if not path.is_absolute():
        path = VAULT_ROOT / path
    path = path.resolve()

    try:
        path.relative_to(VAULT_ROOT)
    except ValueError:
        sys.exit(f"Refusing to publish a file outside the vault: {path}")

    private_dir = VAULT_ROOT / "_private"
    try:
        path.relative_to(private_dir)
        sys.exit("Refusing to publish notes from _private/.")
    except ValueError:
        pass

    if path.suffix.lower() != ".md":
        sys.exit("Source file must be a Markdown file ending in .md.")
    if not path.exists():
        sys.exit(f"Source file does not exist: {path}")
    return path


def strip_frontmatter(markdown: str) -> str:
    if markdown.startswith("---\n"):
        end = markdown.find("\n---", 4)
        if end != -1:
            after = markdown.find("\n", end + 4)
            if after != -1:
                return markdown[after + 1 :]
    return markdown


def first_heading(markdown: str) -> str | None:
    for line in markdown.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return None


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "note"


def plain_summary(markdown: str) -> str:
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("```") or line.startswith(">"):
            continue
        line = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", line)
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"[*_`#>-]", "", line).strip()
        if line:
            return line[:140]
    return "一篇来自 Cedric Notes 的公开笔记。"


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    escaped = re.sub(r'<a href="file://[^"]+">([^<]+)</a>', r"<code>\1</code>", escaped)
    escaped = re.sub(r'<a href="/Users/[^"]+">([^<]+)</a>', r"<code>\1</code>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    return escaped


def is_table_separator(line: str) -> bool:
    stripped = line.strip()
    if "|" not in stripped:
        return False
    stripped = stripped.strip("|").strip()
    if not stripped:
        return False
    cells = [cell.strip() for cell in stripped.split("|")]
    return all(re.match(r"^:?-{3,}:?$", cell) for cell in cells)


def split_table_row(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def table_alignments(separator: str, width: int) -> list[str]:
    cells = split_table_row(separator)
    alignments: list[str] = []
    for cell in cells[:width]:
        left = cell.startswith(":")
        right = cell.endswith(":")
        if left and right:
            alignments.append("center")
        elif right:
            alignments.append("right")
        elif left:
            alignments.append("left")
        else:
            alignments.append("")
    while len(alignments) < width:
        alignments.append("")
    return alignments


def render_table(header_line: str, separator_line: str, body_lines: list[str]) -> str:
    headers = split_table_row(header_line)
    alignments = table_alignments(separator_line, len(headers))
    rows = [split_table_row(line) for line in body_lines]

    output = ['<div class="table-wrap">', "<table>"]
    output.append("  <thead>")
    output.append("    <tr>")
    for index, header in enumerate(headers):
        style = f' style="text-align: {alignments[index]}"' if alignments[index] else ""
        output.append(f"      <th{style}>{inline_markdown(header)}</th>")
    output.append("    </tr>")
    output.append("  </thead>")
    if rows:
        output.append("  <tbody>")
        for row in rows:
            output.append("    <tr>")
            for index in range(len(headers)):
                cell = row[index] if index < len(row) else ""
                style = f' style="text-align: {alignments[index]}"' if alignments[index] else ""
                output.append(f"      <td{style}>{inline_markdown(cell)}</td>")
            output.append("    </tr>")
        output.append("  </tbody>")
    output.append("</table>")
    output.append("</div>")
    return "\n".join(output)


def flush_paragraph(parts: list[str], output: list[str]) -> None:
    if parts:
        output.append(f"<p>{inline_markdown(' '.join(parts))}</p>")
        parts.clear()


def flush_list(items: list[str], output: list[str], ordered: bool) -> None:
    if not items:
        return
    tag = "ol" if ordered else "ul"
    output.append(f"<{tag}>")
    for item in items:
        output.append(f"  <li>{inline_markdown(item)}</li>")
    output.append(f"</{tag}>")
    items.clear()


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    list_ordered = False
    in_code = False
    code_lang = ""
    code_lines: list[str] = []
    in_math = False
    math_lines: list[str] = []
    index = 0

    while index < len(lines):
        raw_line = lines[index]
        line = raw_line.rstrip()

        fence = re.match(r"^```(\w+)?\s*$", line)
        if fence:
            if in_code:
                language = f' class="language-{html.escape(code_lang)}"' if code_lang else ""
                output.append(f"<pre><code{language}>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines = []
                code_lang = ""
                in_code = False
            else:
                flush_paragraph(paragraph, output)
                flush_list(list_items, output, list_ordered)
                code_lang = fence.group(1) or ""
                in_code = True
            index += 1
            continue

        if in_code:
            code_lines.append(line)
            index += 1
            continue

        single_line_math = re.match(r"^\s*\$\$(.+?)\$\$\s*$", line)
        if single_line_math:
            flush_paragraph(paragraph, output)
            flush_list(list_items, output, list_ordered)
            output.append(
                '<div class="math-block">\\[\n'
                + html.escape(single_line_math.group(1).strip())
                + "\n\\]</div>"
            )
            index += 1
            continue

        if line.strip() == "$$":
            if in_math:
                output.append('<div class="math-block">\\[\n' + html.escape("\n".join(math_lines)) + "\n\\]</div>")
                math_lines = []
                in_math = False
            else:
                flush_paragraph(paragraph, output)
                flush_list(list_items, output, list_ordered)
                in_math = True
            index += 1
            continue

        if in_math:
            math_lines.append(line)
            index += 1
            continue

        if not line.strip():
            flush_paragraph(paragraph, output)
            flush_list(list_items, output, list_ordered)
            index += 1
            continue

        if index + 1 < len(lines) and "|" in line and is_table_separator(lines[index + 1]):
            flush_paragraph(paragraph, output)
            flush_list(list_items, output, list_ordered)
            body_lines: list[str] = []
            index += 2
            while index < len(lines) and "|" in lines[index].strip() and lines[index].strip():
                body_lines.append(lines[index].rstrip())
                index += 1
            output.append(render_table(line, lines[index - len(body_lines) - 1], body_lines))
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph(paragraph, output)
            flush_list(list_items, output, list_ordered)
            level = min(len(heading.group(1)) + 1, 6)
            output.append(f"<h{level}>{inline_markdown(heading.group(2).strip())}</h{level}>")
            index += 1
            continue

        if re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", line):
            flush_paragraph(paragraph, output)
            flush_list(list_items, output, list_ordered)
            output.append("<hr>")
            index += 1
            continue

        quote = re.match(r"^>\s?(.*)$", line)
        if quote:
            flush_paragraph(paragraph, output)
            flush_list(list_items, output, list_ordered)
            output.append(f"<blockquote>{inline_markdown(quote.group(1))}</blockquote>")
            index += 1
            continue

        unordered = re.match(r"^\s*[-*+]\s+(.+)$", line)
        ordered = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if unordered or ordered:
            flush_paragraph(paragraph, output)
            current_ordered = bool(ordered)
            if list_items and list_ordered != current_ordered:
                flush_list(list_items, output, list_ordered)
            list_ordered = current_ordered
            list_items.append((ordered or unordered).group(1).strip())
            index += 1
            continue

        flush_list(list_items, output, list_ordered)
        paragraph.append(line.strip())
        index += 1

    if in_code:
        language = f' class="language-{html.escape(code_lang)}"' if code_lang else ""
        output.append(f"<pre><code{language}>{html.escape(chr(10).join(code_lines))}</code></pre>")
    if in_math:
        output.append('<div class="math-block">\\[\n' + html.escape("\n".join(math_lines)) + "\n\\]</div>")
    flush_paragraph(paragraph, output)
    flush_list(list_items, output, list_ordered)
    return "\n".join(output)


def render_article(metadata: NoteMetadata, body_html: str) -> str:
    title = html.escape(metadata.title)
    description = html.escape(metadata.description)
    label = html.escape(metadata.label)
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} | Cedric Notes</title>
    <meta name="description" content="{description}">
    <link rel="stylesheet" href="../styles.css">
    <link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
    <script>
      window.MathJax = {{
        tex: {{
          inlineMath: [["$", "$"], ["\\\\(", "\\\\)"]],
          displayMath: [["$$", "$$"], ["\\\\[", "\\\\]"]]
        }},
        svg: {{ fontCache: "global" }}
      }};
    </script>
    <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
  </head>
  <body class="note-page">
    <main class="note-main">
      <a class="note-back" href="../index.html">← Back to Cedric Notes</a>
      <header class="note-header">
        <p class="note-meta">{label}</p>
        <h1>{title}</h1>
        <p class="note-lede">{description}</p>
      </header>
      <article class="note-content">
{indent_html(body_html, 8)}
      </article>
    </main>
  </body>
</html>
"""


def indent_html(markup: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(f"{prefix}{line}" if line else "" for line in markup.splitlines())


def post_entry(metadata: NoteMetadata) -> str:
    return f"""          <article class="post-row" data-category="{html.escape(metadata.category)}">
            <div>
              <p class="post-meta">{html.escape(metadata.label)}</p>
              <h3>{html.escape(metadata.title)}</h3>
              <p>{html.escape(metadata.description)}</p>
            </div>
            <a href="./notes/{html.escape(metadata.slug)}.html">Open</a>
          </article>
"""


def update_index(metadata: NoteMetadata) -> bool:
    index = INDEX_PATH.read_text(encoding="utf-8")
    href = f'./notes/{metadata.slug}.html'
    if href in index:
        return False

    marker = '        <div class="post-list" id="postList">\n'
    if marker not in index:
        sys.exit("Could not find the homepage post list insertion point.")
    index = index.replace(marker, marker + post_entry(metadata), 1)
    INDEX_PATH.write_text(index, encoding="utf-8")
    return True


def main() -> None:
    args = parse_args()
    source = resolve_source(args.source)
    raw_markdown = source.read_text(encoding="utf-8")
    markdown = strip_frontmatter(raw_markdown).strip()

    title = args.title or first_heading(markdown) or source.stem
    slug = args.slug or slugify(title)
    description = args.description or plain_summary(markdown)
    label = args.label or CATEGORY_LABELS[args.category]
    metadata = NoteMetadata(
        title=title,
        description=description,
        category=args.category,
        label=label,
        slug=slug,
    )

    output_path = NOTES_DIR / f"{metadata.slug}.html"
    if output_path.exists() and not args.force:
        sys.exit(f"Output already exists: {output_path}. Use --force to overwrite it.")

    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_article(metadata, markdown_to_html(markdown)), encoding="utf-8")

    index_updated = False
    if not args.no_index:
        index_updated = update_index(metadata)

    print(f"Published: {output_path.relative_to(VAULT_ROOT)}")
    print(f"Homepage updated: {'yes' if index_updated else 'no'}")


if __name__ == "__main__":
    main()
