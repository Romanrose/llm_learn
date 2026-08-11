# Stanford CS336 lectures upstream

`lectures/` is a vendored snapshot of the Stanford CS336 lecture repository. Its files are intentionally tracked as normal files by this repository, so cloning `Romanrose/llm_learn` provides the full course material without a submodule checkout step.

- Upstream: <https://github.com/stanford-cs336/lectures.git>
- Snapshot commit: `8b59b50730766695c2ffedd1a79c50cd09b9eb91`
- Snapshot date: 2026-05-27

## Updating the snapshot

Clone the upstream repository into a temporary directory, compare it with `lectures/`, and review the changes before copying anything. Do not initialise a nested Git repository inside `lectures/`.

```bash
git clone --depth 1 https://github.com/stanford-cs336/lectures.git /tmp/cs336-lectures-upstream
diff -rq /tmp/cs336-lectures-upstream llm/cs336-2026/lectures
```
