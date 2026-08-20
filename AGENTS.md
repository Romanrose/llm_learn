# Agent Instructions for `llm_learn`

## Purpose and current scope

This repository is a course-first learning knowledge base. The primary public product is the VitePress site at <https://romanrose.github.io/llm_learn/>.

- **CS336 2026** is the reference implementation for a complete course workspace: official resources, lecture notes, Blog explanations, English/Chinese transcripts, references, and PDF exports.
- **CS149 Fall 2025** currently publishes only course resources and lecture navigation. Its notes, Blog posts, and transcripts are private until explicitly enabled.
- `agent/`, `infra/`, `papers/`, and `interest/` contain project or topic material. Treat them as source repositories or short learning-note entries; do not force them into the course-lecture workflow unless asked.

## Active paths

Use these paths for current work:

- `website/`: VitePress content, theme, navigation, homepage, and topic entry pages.
- `website/catalog-data/courses/<course-id>.yaml`: authoritative course/lecture metadata and public `outputs`.
- `llm/<course-id>/notes/<lecture-id>/`: CS336-style lecture content and review records.
- `infra/cs149-fall25/`: CS149 materials, resource manifest, and future notes.
- `workflow/scripts/`: Course CLI, website generator, and LaTeX export scripts.
- `workflow/standards/`: project structure, transcript, and prompt requirements.

`website/generated/` and `website/.vitepress/generated/` are generated. Never edit them directly; update the source Markdown, YAML, Vue/CSS, or generator and rerun generation.

Older `site/`, `catalog/`, and `scripts/` directories are not the active website pipeline. Do not add new website work there unless a migration task explicitly requires it.

## Content and publication rules

1. Keep a stable `course-id` and `lecture-id` across source folders, catalog metadata, generated routes, and review records.
2. A public course page is controlled by `website/catalog-data/courses/<course-id>.yaml`; do not infer publication from the mere existence of a local Markdown file.
3. Add a Lecture Note, Blog, or transcript to `outputs` only after the content has been reviewed. Candidate content belongs under the lecture's `references/<provider>/` directory.
4. Preserve the boundary between content types:
   - `transcript.en.md` / `transcript.zh-CN.md`: complete, timestamped transcript.
   - `note.md`: structured lecture interpretation.
   - `blog.md`: independent reader-facing explanation.
5. Do not download video/audio or invoke ASR unless the user explicitly authorizes audio download. Prefer official or platform subtitles.
6. Keep official slides, videos, papers, repositories, and external projects as links unless their license and the task explicitly permit a local copy.
7. Do not expose API keys, cookies, local paths, private URLs, or model credentials. Use `.env` locally; never commit it.

For details, read `workflow/standards/project-structure.md` and `workflow/standards/transcript-generation.md` before changing course content.

## Website conventions

- The homepage is a lightweight navigator. Courses receive full workspaces; projects and topics generally receive concise links or project-note entries.
- Scope course sidebars by course route. A CS336 page must not show CS149's lecture list, and vice versa.
- Keep the interface minimal, readable, and information-dense. Avoid introducing dashboard widgets, large marketing heroes, duplicate entry points, or decorative cards unless explicitly requested.
- Preserve the white-background course-library visual direction and existing VitePress theme conventions.

## Commands

```bash
npm install
npm run dev
npm run build

# Course workflow
npm run course -- sync <course-id>
npm run course -- discover <course-id>
npm run course -- prepare <course-id> <lecture-id>
npm run course -- transcript <course-id> <lecture-id> --engine krillinai --dry-run
npm run course -- generate <course-id> <lecture-id> --provider deepseek --run
npm run course -- validate <course-id> <lecture-id> --provider deepseek
npm run course -- promote <course-id> <lecture-id> --provider deepseek --reviewed --overwrite
npm run course -- export <course-id> <lecture-id>
```

Run `npm run build` after changes that affect catalog data, the generator, VitePress configuration, or site styling. The build regenerates site files and exports configured PDFs.

## Safe working practices

- Inspect `git status` before editing. Preserve unrelated user changes and untracked files.
- Do not use destructive Git operations or bulk deletes to obtain a clean tree.
- Use targeted edits and stage only files belonging to the requested change.
- Do not commit, push, create pull requests, change repository metadata, or deploy unless the user explicitly asks for that external action.
- If a user request conflicts with these instructions, follow the user's request and record the resulting scope clearly in the affected documentation.
