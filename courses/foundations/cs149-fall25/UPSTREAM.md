# CS149 Fall 2025 上游资料

本课程不 vendor 上游仓库或镜像 PDF；课程 Slides 由 Stanford 页面托管，仓库只保留经过审核的 URL、来源时间和后续学习产物。

- 课程信息：<https://gfxcourses.stanford.edu/cs149/fall25/courseinfo>
- 讲义目录：<https://gfxcourses.stanford.edu/cs149/fall25/lecture/>
- 公开视频（2023 版本）：<https://www.youtube.com/playlist?list=PLoROMvodv4rMp7MTFr4hQsDEcX7Bx6Odp>
- 本次资料核对：2026-08-18

## 更新方式

1. 打开课程信息页和讲义目录，确认学期、讲数与每讲的 PDF 链接。
2. 更新 `website/catalog-data/courses/cs149-fall25.yaml`，不要手改 `website/generated/`。
3. 执行 `npm run course -- discover cs149-fall25`，审核 `website/catalog-data/reviews/` 中新增或变更的链接。
4. 默认只摄取清单；确有保存必要且确认课程方许可后，才使用 `npm run course -- ingest cs149-fall25 --download`。

课程内容、讲义和作业的版权归 Stanford 及原作者所有；本目录的中文学习笔记和自写代码应单独标明来源与引用。
