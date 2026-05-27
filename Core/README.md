# Personal Blog Website

这是从当前 Obsidian Vault 生成的个人博客静态站点，用于公开展示项目、学习研究和思考输出。

## Files

- `index.html`：站点首页，包含项目、文章索引、学习栏目和关于区域。
- `styles.css`：视觉风格，参考 Apple 官网的大留白与产品化层级、Anthropic 的克制内容结构、Dan Koe 站点的个人创作者式入口。
- `notes/`：公开文章页，按 `projects/`、`writing/`、`learning/` 及其子分类存放。
- `collections/`：二级分类页，例如数学、经济学、哲学、研究报告和项目集合。
- `assets/knowledge-map.svg`：首页知识地图视觉资产。

## Usage

直接在浏览器中打开 `index.html` 即可预览。

如果发布到 GitHub Pages，可以把 Pages source 设置为 `main` 分支的仓库根目录。根目录的 `index.html` 会自动跳转到 `Core/` 下的博客页面。

## Update Workflow

1. 新增公开笔记优先使用 `Core/tools/publish_note.py`。
2. 文章页放在 `notes/projects/`、`notes/writing/` 或 `notes/learning/` 下的对应子分类。
3. 新增主题板块后，在对应的 Projects、Writing 或 Learning 区域添加入口。
4. 项目有阶段性成果后，更新 Selected projects 区域。
5. 不要链接 `_private/` 中的内容。

## Publish a Markdown Note

使用发布脚本可以把 Vault 内的 Markdown 笔记完整转换成博客风格的 HTML 页面，并自动加入首页对应列表。
脚本支持常见 Markdown 结构，包括标题、段落、列表、代码块、引用、分隔线、表格、链接、基础强调语法，以及由 MathJax 渲染的 `$...$`、`$$...$$` 数学公式。

示例：

```bash
python3 Core/tools/publish_note.py \
  "03_Areas/Philosophy/审美目的论的实践论.md" \
  --category philosophy \
  --slug aesthetic-practice-full \
  --description "把审美目的论推进到实践、选择与生活形式。"
```

常用参数：

- `--category`：首页筛选分类，可选 `project`、`philosophy`、`learning`。
- `--slug`：输出文件名，不含 `.html`。
- `--title`：覆盖文章标题；默认使用 Markdown 第一个一级标题或文件名。
- `--description`：首页摘要和文章导语。
- `--label`：文章小标签。
- `--force`：允许覆盖已经生成的同名 HTML。
- `--no-index`：只生成文章页，不更新首页。
- `--collection`：可选，把文章加入对应大类下的二级分类页，例如 `mathematics`、`economics`、`philosophy`、`projects`。
- `--collection-section`：分类页中的板块标题，例如 `代数学`、`分析学`、`审美目的论`、`马克思主义`。
- `--output-dir`：可选，手动指定 `notes/` 下的输出目录，例如 `learning/mathematics/algebra`。

脚本会拒绝发布 `_private/` 下的文件。

示例：发布到“数学 / 代数学”：

```bash
python3 Core/tools/publish_note.py \
  "04_Resources/Mathe/Algèbre Ch2 Sous-espaces vectoriels.md" \
  --category learning \
  --slug algebra-subspaces \
  --description "向量子空间、线性组合、基与维数。" \
  --collection mathematics \
  --collection-section 代数学
```
