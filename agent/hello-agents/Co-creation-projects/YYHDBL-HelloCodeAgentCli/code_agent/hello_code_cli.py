from __future__ import annotations

import argparse
import os
import re
import logging
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover
    def load_dotenv(*args, **kwargs):  # type: ignore
        return False

from core.llm import HelloAgentsLLM
from core.exceptions import HelloAgentsException
from core.config import Config
from code_agent.agentic import CodeAgent
from code_agent.executors.apply_patch_executor import ApplyPatchExecutor, PatchApplyError
from utils.cli_ui import c, hr, PRIMARY, ACCENT, INFO, WARN, ERROR


# 匹配 Codex 风格补丁块（宽松，跨行，允许前导空白或代码围栏）
PATCH_RE = re.compile(r"\s*\*\*\* Begin Patch[\s\S]*?\*\*\* End Patch", re.MULTILINE)
# 备用：从 ```patch/```diff 围栏中提取补丁主体
PATCH_FENCE_RE = re.compile(
    r"```(?:patch|diff|text)?\s*(\*\*\* Begin Patch[\s\S]*?\*\*\* End Patch)\s*```",
    re.MULTILINE,
)


def _extract_patch(text: str) -> str | None:
    """
    从 LLM 响应文本中提取补丁块。
    补丁块通常由 *** Begin Patch 和 *** End Patch 包围。
    """
    # 优先匹配代码围栏内的补丁
    m = PATCH_FENCE_RE.search(text)
    if m:
        return m.group(1)
    # 退回普通匹配（允许前导空白）
    m = PATCH_RE.search(text)
    return m.group(0).strip() if m else None


def _normalize_patch(patch_text: str) -> str:
    """
    规范化补丁文本，以宽容处理模型的一些格式错误。
    - 接受 'Delete File:' / 'Update File:' / 'Add File:' (即使缺少前导 '*** ')
    - 保持执行器所需的标准 Codex 风格格式。
    """
    lines = patch_text.splitlines()
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("Add File:", "Update File:", "Delete File:")) and not stripped.startswith("*** "):
            out.append("*** " + stripped)
            continue
        out.append(line)
    return "\n".join(out)


def _patch_requires_confirmation(patch_text: str) -> bool:
    """
    判断补丁是否需要用户确认。
    策略：
    - 包含文件删除操作
    - 涉及文件数量过多 (>= 6)
    - 变更行数过多 (>= 400)
    """
    # MVP: Delete File / too many files / too big => confirm
    if "*** Delete File:" in patch_text:
        return True
    file_ops = patch_text.count("*** Add File:") + patch_text.count("*** Update File:") + patch_text.count("*** Delete File:")
    if file_ops >= 6:
        return True
    changed_lines = 0
    for line in patch_text.splitlines():
        if line.startswith("+") or line.startswith("-"):
            changed_lines += 1
    return changed_lines >= 400


def main(argv: list[str] | None = None) -> int:
    """
    CLI 入口点。
    初始化 LLM、CodebaseMaintainer 和 PatchExecutor，并进入交互式循环。
    """
    # 1. 解析命令行参数
    parser = argparse.ArgumentParser(description="HelloAgents-style Code Agent CLI (Codex/Claude-like)")
    parser.add_argument("--repo", type=str, default=".", help="Repository root (workspace). Default: .")
    parser.add_argument("--project", type=str, default=None, help="Project name (default: repo folder name)")
    args = parser.parse_args(argv)

    # 2. 初始化环境和 LLM
    repo_root = Path(args.repo).resolve()
    load_dotenv(dotenv_path=repo_root / ".env", override=False)

    project = args.project or repo_root.name
    config = Config.from_env()
    llm = HelloAgentsLLM()  # auto-detect provider from env
    # reduce noisy HTTP client logs in the CLI
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("openai._base_client").setLevel(logging.WARNING)
    logging.getLogger("memory").setLevel(logging.WARNING)

    print(c(hr("=", 80), INFO))
    print(c("HelloAgents Code Agent CLI", PRIMARY))
    print(c(f"workspace: {repo_root}", INFO))
    print(c(f"LLM: provider={llm.provider} model={llm.model} base_url={llm.base_url}", INFO))
    print(c(f"state: {Path(config.helloagents_dir).as_posix()}", INFO))
    print(c(hr("=", 80), INFO))

    # Optional preflight to surface auth issues early.
    try:
        _ = llm.invoke([{"role": "user", "content": "ping"}], max_tokens=1)
    except HelloAgentsException as e:
        print(c("LLM 预检失败（通常是 API key/base_url/model 配置问题）。", ERROR))
        print(c(f"error: {e}", ERROR))
        print(c("请检查 .env 中的 DEEPSEEK_API_KEY / LLM_* 配置是否正确。", WARN))
        return 2

    # 3. 初始化核心组件（ReAct + tools）
    agent = CodeAgent(repo_root=repo_root, llm=llm, config=config)
    patch_executor = ApplyPatchExecutor(repo_root=repo_root)

    # 4. 进入交互循环
    print(c("输入自然语言需求开始；命令：", INFO))
    print(c("  :quit", ACCENT) + c(" 退出", INFO))
    print(c("  :plan <目标>", ACCENT) + c(" 强制生成计划", INFO))
    while True:
        try:
            user_in = input(c("👤 > ", PRIMARY))
        except (EOFError, KeyboardInterrupt):
            print("\n" + c("bye", INFO))
            return 0

        if user_in is None:
            continue
        user_in = user_in.strip()
        if not user_in:
            print(c("请提供具体指令或问题。", WARN))
            continue
        if user_in in {":q", ":quit", "quit", "exit"}:
            print(c("bye", INFO))
            return 0
        if user_in.startswith(":plan"):
            goal = user_in[len(":plan") :].strip() or "请为当前任务生成一个可执行计划"
            response = agent.registry.execute_tool("plan", goal)
            print("\n" + c("🤖 plan", PRIMARY))
            print(response + "\n")
            continue

        # 5. 运行一轮对话（ReAct 可能按需调用终端/笔记/记忆）
        try:
            response = agent.run_turn(user_in)
        except HelloAgentsException as e:
            print(c(f"LLM 调用失败: {e}", ERROR))
            continue

        # 对于 direct reply（未经过 ReAct 的控制台打印），在 CLI 里补打一份输出
        if getattr(agent, "last_direct_reply", False):
            print(c("🤖 assistant", PRIMARY))
            print(response)
        
        # 7. 提取并应用补丁
        patch_text = _extract_patch(response)
        if not patch_text:
            continue
        patch_text = _normalize_patch(patch_text)
        # Ignore empty patch blocks
        if patch_text.strip() == "*** Begin Patch\n*** End Patch":
            continue

        needs_confirm = _patch_requires_confirmation(patch_text)
        if needs_confirm:
            # If user just answered y/n as the *current* input, treat it as confirmation for this patch.
            if user_in.strip().lower() in {"n", "no"}:
                print("已取消补丁应用。")
                continue
            if user_in.strip().lower() not in {"y", "yes"}:
                print("\n⚠️ 检测到高风险补丁（删除/大规模变更）。是否应用？(y/n)")
                ans = input("confirm> ").strip().lower()
                if ans not in {"y", "yes"}:
                    print("已取消补丁应用。")
                    continue

        try:
            res = patch_executor.apply(patch_text)
            print("\n" + c("✅ Patch applied", PRIMARY))
            print(c(f"files: {', '.join(res.files_changed) if res.files_changed else '(none)'}", INFO))
            if res.backups:
                print(c(f"backups: {len(res.backups)} (in .helloagents/backups/...)", INFO))

            # 记录到 NoteTool（action）
            agent.note_tool.run({
                "action": "create",
                "title": "Patch applied",
                "content": f"User input:\n{user_in}\n\nPatch:\n\n```text\n{patch_text}\n```\n\nFiles:\n"
                + "\n".join([f"- {p}" for p in res.files_changed]),
                "note_type": "action",
                "tags": [project, "patch_applied"],
            })
        except PatchApplyError as e:
            print("\n" + c(f"❌ Patch failed: {e}", ERROR))
            agent.note_tool.run({
                "action": "create",
                "title": "Patch failed",
                "content": f"Error: {e}\n\nUser input:\n{user_in}\n\nPatch:\n\n```text\n{patch_text}\n```\n",
                "note_type": "blocker",
                "tags": [project, "patch_failed"],
            })
            continue

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
