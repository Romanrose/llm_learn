# 可复现课程工作流

课程自动化脚本、安装方式和质量门禁都在本仓库中；虚拟环境、二进制、媒体下载、缓存与密钥始终保留在本机。

## 首次安装

前提：Node.js、npm 和 [uv](https://docs.astral.sh/uv/) 可用。

```bash
npm install
npm run workflow:bootstrap
npm run workflow:doctor
```

`workflow:bootstrap` 在 `workflow/.runtime/` 创建隔离 Python 环境并安装（或更新）满足最低版本的 `yt-dlp`。视频平台变化频繁，因此每次重新执行 bootstrap 都会刷新下载器；该目录被 Git 忽略，任何人 clone 后都能独立创建；不要提交它。

复制 `.env.example` 为 `.env`。保留 `COURSE_YT_DLP` 为空即可使用 bootstrap 的默认位置。DeepSeek、OpenAI、KrillinAI 和 Codex CLI 均为可选能力；分别在确有需要时配置自己的凭据或路径，绝不共享 `.env`、Cookie 或二进制文件。

## 工作流

```text
discover → approve → ingest → prepare → generate → validate → 人工审核 → promote → build
```

- `discover`：从课程入口发现候选链接，写入审核清单。
- `approve`：明确批准需要进入知识库的公开资源。
- `ingest`：默认只保存审核后的链接；只有显式传入 `--download` 才下载二进制资料。
- `prepare`：用 `yt-dlp` 查询视频并优先下载平台字幕，不下载音频或视频；仓库自带的字幕清洗器将 VTT/SRT 转为带时间戳的英文稿。
- `generate`：生成候选翻译、Lecture Note 与 Blog。需要 Codex CLI 或配置的 DeepSeek API。
- `validate`：检查文件、时间戳、重复与长度异常。
- `promote --reviewed`：只有人工审核确认后才将候选稿登记为正式公开产物。

没有可用字幕时，流程会停止在 `needs-audio-authorization`。下载音频或使用 ASR 前必须取得用户的明确授权。

## 常用命令

```bash
npm run course -- discover <course-id>
npm run course -- prepare <course-id> <lecture-id>
npm run course -- generate <course-id> <lecture-id> --provider deepseek --run
npm run course -- validate <course-id> <lecture-id> --provider deepseek
# 人工审核后
npm run course -- promote <course-id> <lecture-id> --provider deepseek --reviewed
npm run build
```

`npm run workflow:subtitle -- --help` 可单独检查字幕下载与清洗器的用法。它只请求平台字幕轨道，不包含音频或视频下载逻辑。

## 可选 KrillinAI

KrillinAI 不随仓库发布。自行安装后在 `.env` 中设置 `COURSE_KRILLINAI`，再运行：

```bash
npm run course -- transcript <course-id> <lecture-id> --engine krillinai --dry-run
```

若选择可能回退到 ASR 的字幕来源，还必须显式增加 `--allow-audio-download`。
