import subprocess
import shlex
import os

class TerminalTool:
    name = "terminal_exec"
    description = "执行终端命令查看目录、文件和系统信息（支持：pwd, ls, cat, echo, whoami, date等）"

    def __init__(self, security_mode="strict"):
        """
        初始化终端工具
        
        Args:
            security_mode: "strict"（严格模式，直接拒绝） 或 "warning"（警告模式，给出提示）
        """
        self.security_mode = security_mode
        
        # 扩展的白名单命令列表（无参数或安全参数的命令）
        self.allowed_commands = {
            "ls": [],  # ls 可以带参数如 -l, -a
            "pwd": [],
            "echo": ["*"],  # echo 允许任何参数
            "whoami": [],
            "cat": ["*"],  # cat 允许文件名参数
            "head": ["-n"],  # head 允许 -n 参数
            "tail": ["-n"],
            "wc": ["-l", "-w"],
            "date": [],
            "uname": ["-a"],
            "find": ["."],  # 限制搜索起点
            # 新增的常用安全命令
            "cd": [],  # 目录切换
            "mkdir": ["-p"],  # 创建目录
            "touch": [],  # 创建文件
            "grep": ["-i", "-n", "-r"],  # 文本搜索
            "which": [],  # 查找命令位置
            "whereis": [],  # 查找程序位置
            "du": ["-h", "-s"],  # 磁盘使用情况
            "df": ["-h"],  # 文件系统信息
        }
        
        # 危险关键词，用于额外安全检查
        self.dangerous_keywords = [
            "rm", "delete", "del", "format", "mkfs",
            "sudo", "su", "passwd", "chmod", "chown",
            "dd", "mkfs", "fdisk", ">", ">>", "|",
            ";", "&&", "||", "`", "$(", "eval"
        ]

    def get_parameters(self):
        return {
            "input": {
                "type": "str", 
                "description": "输入终端命令，如：pwd, ls -la, cat filename.txt", 
                "required": True,
                "examples": ["pwd", "ls -la", "cat README.md", "echo hello", "whoami", "date"]
            }
        }

    def _check_command_safety(self, cmd):
        """检查命令安全性
        
        Returns:
            tuple: (is_safe, error_msg, warning_msg)
                is_safe: bool - 是否安全
                error_msg: str - 错误消息
                warning_msg: str - 警告消息
        """
        # 检查危险关键词
        cmd_lower = cmd.lower()
        for keyword in self.dangerous_keywords:
            if keyword in cmd_lower:
                error_msg = f"检测到不安全的操作：{keyword}"
                warning_msg = f"⚠️ 警告：此命令包含 '{keyword}' 操作，可能导致系统损坏或数据丢失！"
                return False, error_msg, warning_msg
        
        # 检查是否包含管道、重定向等操作
        operators = ["|", ">", "<", "&", "&&", "||", ";"]
        for op in operators:
            if op in cmd:
                error_msg = f"检测到不安全的操作符：{op}"
                warning_msg = f"⚠️ 警告：此命令包含 '{op}' 操作符，可能导致意外行为！"
                return False, error_msg, warning_msg
        
        return True, None, None

    def run(self, parameters):
        # 确保参数处理的安全性
        if isinstance(parameters, dict):
            # 统一使用 {"input": command} 格式
            cmd = parameters.get("input", "")
        else:
            cmd = str(parameters) if parameters else ""

        cmd = cmd.strip() if cmd else ""
        
        if not cmd:
            return "错误: 命令不能为空"
        
        # 安全检查
        is_safe, error_msg, warning_msg = self._check_command_safety(cmd)
        if not is_safe:
            if self.security_mode == "strict":
                return f"🚫 安全拒绝: {error_msg}"
            else:  # warning mode
                return f"{warning_msg}\n\n命令: {cmd}\n\n如需继续执行，请确认操作的安全性。\n(当前为警告模式，尚未真正执行)"
        
        # 分割命令和参数
        parts = shlex.split(cmd)
        if not parts:
            return "错误: 无效的命令"
        
        command_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # 检查命令是否在白名单中
        if command_name not in self.allowed_commands:
            allowed_list = ", ".join(sorted(self.allowed_commands.keys()))
            similar_commands = self._find_similar_commands(command_name)
            error_msg = f"🚫 命令 '{command_name}' 不在允许列表中。"
            error_msg += f"\n\n✅ 允许的命令: {allowed_list}"
            if similar_commands:
                error_msg += f"\n💡 您是否想使用: {', '.join(similar_commands)}?"
            error_msg += f"\n\n📖 输入 'help' 或 '?' 查看命令帮助"
            return error_msg
        
        # 检查参数
        allowed_args = self.allowed_commands[command_name]
        
        # 改进的参数验证逻辑
        if "*" not in allowed_args and args:
            validation_result = self._validate_parameters(command_name, args)
            if not validation_result[0]:  # 验证失败
                return validation_result[1]
        
        # 如果允许任何参数，进行基本安全检查
        elif "*" in allowed_args and args:
            validation_result = self._validate_wildcard_args(command_name, args)
            if not validation_result[0]:  # 验证失败
                return validation_result[1]
        
        # 执行命令（使用 shell=False 提高安全性）
        try:
            # 使用 shlex.split 可以正确处理带引号的参数
            result = subprocess.run(
                cmd,
                shell=True,  # 保持向后兼容，但需要更严格的白名单
                capture_output=True,
                text=True,
                timeout=15,
                cwd=None  # 限制在安全目录执行
            )
            
            # 组合标准输出和标准错误
            output = result.stdout
            if result.stderr:
                output += f"\n[标准错误]\n{result.stderr}"
            
            # 返回执行结果
            if result.returncode == 0:
                return output.strip() if output.strip() else "命令执行成功（无输出）"
            else:
                return f"命令执行失败 (返回码: {result.returncode})\n{output.strip()}"
                
        except subprocess.TimeoutExpired:
            return "命令执行超时（超过15秒）。"
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr
            return f"命令执行错误: {error_output or str(e)}"
        except Exception as e:
            return f"执行异常: {str(e)}"

    def _validate_parameters(self, command_name, args):
        """验证特定命令的参数
        
        Args:
            command_name: 命令名称
            args: 参数列表
            
        Returns:
            tuple: (is_valid, error_message)
        """
        allowed_args = self.allowed_commands[command_name]
        
        # 验证选项参数
        option_args = [arg for arg in args if arg.startswith("-")]
        for arg in option_args:
            if arg not in allowed_args and arg != "-p":  # -p 是特殊的，允许mkdir使用
                help_text = self._get_command_help(command_name)
                return False, f"参数 '{arg}' 不被允许。\n{help_text}"
        
        # 验证非选项参数（通常是文件路径）
        file_args = [arg for arg in args if not arg.startswith("-")]
        for arg in file_args:
            if self._is_dangerous_path(arg):
                return False, f"危险路径: {arg}\n只允许访问当前目录及其子目录"
        
        return True, None

    def _validate_wildcard_args(self, command_name, args):
        """验证通配符参数（适用于cat、echo等）
        
        Args:
            command_name: 命令名称
            args: 参数列表
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # 对于文件操作命令，进行路径安全检查
        if command_name in ["cat", "head", "tail", "grep"]:
            for arg in args:
                if not arg.startswith("-") and self._is_dangerous_path(arg):
                    return False, f"危险路径: {arg}\n只允许访问当前目录及其子目录"
        
        return True, None

    def _is_dangerous_path(self, path):
        """检查路径是否危险
        
        Args:
            path: 要检查的路径
            
        Returns:
            bool: 是否为危险路径
        """
        # 检查绝对路径
        if os.path.isabs(path):
            return True
        
        # 检查包含危险字符的路径
        dangerous_patterns = ["../", "..\\", "~/", "/etc", "/bin", "/usr", "/var", "/sys"]
        for pattern in dangerous_patterns:
            if pattern in path:
                return True
        
        return False

    def _get_command_help(self, command_name):
        """返回命令的使用帮助
        
        Args:
            command_name: 命令名称
            
        Returns:
            str: 帮助信息
        """
        help_text = {
            "pwd": "用法: pwd\n功能: 显示当前工作目录",
            "ls": "用法: ls [-la] [路径]\n功能: 列出目录内容\n选项: -l(详细信息), -a(显示隐藏文件)",
            "cat": "用法: cat <文件名>\n功能: 显示文件内容",
            "head": "用法: head [-n 行数] <文件>\n功能: 显示文件开头内容",
            "tail": "用法: tail [-n 行数] <文件>\n功能: 显示文件末尾内容",
            "wc": "用法: wc [-l|-w] <文件>\n功能: 统计文件行数、字数\n选项: -l(行数), -w(字数)",
            "echo": "用法: echo <文本>\n功能: 输出文本",
            "whoami": "用法: whoami\n功能: 显示当前用户名",
            "date": "用法: date\n功能: 显示当前日期时间",
            "uname": "用法: uname [-a]\n功能: 显示系统信息\n选项: -a(所有信息)",
            "find": "用法: find . [选项]\n功能: 查找文件\n注意: 只能在当前目录搜索",
            "cd": "用法: cd <目录>\n功能: 切换到指定目录",
            "mkdir": "用法: mkdir [-p] <目录名>\n功能: 创建目录\n选项: -p(递归创建)",
            "touch": "用法: touch <文件名>\n功能: 创建空文件",
            "grep": "用法: grep [-inr] '模式' <文件>\n功能: 搜索文本\n选项: -i(忽略大小写), -n(显示行号), -r(递归)",
            "which": "用法: which <命令>\n功能: 查找命令位置",
            "whereis": "用法: whereis <程序>\n功能: 查找程序位置",
            "du": "用法: du [-hs] [路径]\n功能: 显示磁盘使用情况\n选项: -h(人类可读), -s(总计)",
            "df": "用法: df [-h]\n功能: 显示文件系统信息\n选项: -h(人类可读)"
        }
        return help_text.get(command_name, f"命令 '{command_name}' 暂无帮助信息")

    def _find_similar_commands(self, command_name):
        """查找相似的命令名称
        
        Args:
            command_name: 输入的命令名称
            
        Returns:
            list: 相似命令列表
        """
        import difflib
        
        # 获取所有允许的命令
        allowed_commands = list(self.allowed_commands.keys())
        
        # 使用difflib查找相似命令
        similar = difflib.get_close_matches(command_name, allowed_commands, n=3, cutoff=0.6)
        
        return similar
