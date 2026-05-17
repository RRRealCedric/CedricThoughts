# Personal Blog Website

这是从当前 Obsidian Vault 生成的个人博客静态站点，用于公开展示项目、学习研究和思考输出。

## Files

- `index.html`：站点首页，包含项目、文章索引、学习栏目和关于区域。
- `styles.css`：视觉风格，参考 Apple 官网的大留白与产品化层级、Anthropic 的克制内容结构、Dan Koe 站点的个人创作者式入口。
- `script.js`：文章分类筛选交互。
- `assets/knowledge-map.svg`：首页知识地图视觉资产。

## Usage

直接在浏览器中打开 `index.html` 即可预览。

如果发布到 GitHub Pages，可以把 Pages source 设置为 `main` 分支的仓库根目录。根目录的 `index.html` 会自动跳转到本博客页面。

## Update Workflow

1. 新增公开笔记后，在 `index.html` 的 Writing 区域添加一条 `post-row`。
2. 新增长期栏目后，在 Knowledge map 区域添加对应 MOC 链接。
3. 项目有阶段性成果后，更新 Selected projects 区域。
4. 不要链接 `_private/` 中的内容。

## Publish a Markdown Note

使用发布脚本可以把 Vault 内的 Markdown 笔记完整转换成博客风格的 HTML 页面，并自动加入首页 Writing 列表。

示例：

```bash
python3 06_Outputs/personal-blog/tools/publish_note.py \
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

脚本会拒绝发布 `_private/` 下的文件。
