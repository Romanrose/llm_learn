# llm_learn LaTeX 输出模板

这里保存项目内可复现的 XeLaTeX 输出样式，不依赖仓库外部的模板目录。

- `mi-core.sty`：字体、颜色、公式、提示框、代码和通用宏。
- `mi-book.sty`：6 × 9 英寸课程讲义版式。

课程内容通过 `npm run course -- export <course-id> <lecture-id>` 生成到对应课程的 `exports/latex/` 目录。导出的目录包含 `.tex`、样式和图片，可以独立下载后编译。

网站构建会自动导出 catalog 中声明了 `exports` 的 Lecture。GitHub Actions 通过 XeLaTeX 工具链生成 PDF；本地编译时需要安装 XeLaTeX、中文字体和 `tcolorbox` 等 LaTeX 依赖。生成的 PDF、`.tex` 和 `site/public/generated/` 内容均为构建产物，不提交 Git。
