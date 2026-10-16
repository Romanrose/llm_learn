"""
人工验证界面

使用Gradio创建Web界面，用于人工验证生成的AIME题目
"""

import json
import os
from typing import List, Dict, Any, Tuple
from datetime import datetime
import gradio as gr


class HumanVerificationUI:
    """人工验证界面"""
    
    def __init__(self, data_path: str):
        """
        初始化验证界面
        
        Args:
            data_path: 生成数据的JSON文件路径
        """
        self.data_path = data_path
        self.problems = self._load_problems()
        self.current_index = 0
        self.verifications = self._load_verifications()
        
    def _load_problems(self) -> List[Dict[str, Any]]:
        """加载题目数据"""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"数据文件不存在: {self.data_path}")
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_verifications(self) -> Dict[str, Any]:
        """加载已有的验证结果"""
        verification_path = self.data_path.replace(".json", "_verifications.json")
        
        if os.path.exists(verification_path):
            with open(verification_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {}
    
    def _save_verifications(self):
        """保存验证结果"""
        verification_path = self.data_path.replace(".json", "_verifications.json")
        
        with open(verification_path, 'w', encoding='utf-8') as f:
            json.dump(self.verifications, f, ensure_ascii=False, indent=2)
    
    def get_current_problem(self) -> Tuple[str, str, str, str, str, str]:
        """获取当前题目信息"""
        if not self.problems:
            return "无题目", "", "", "", "", "0/0"

        problem = self.problems[self.current_index]
        problem_id = problem.get("id", "unknown")

        # 获取已有的验证信息
        verification = self.verifications.get(problem_id, {})

        return (
            f"题目 {self.current_index + 1}/{len(self.problems)}",
            problem.get("problem", ""),
            f"答案: {problem.get('answer', 'N/A')}",
            problem.get("solution", ""),
            f"主题: {problem.get('topic', 'N/A')}",
            verification.get("comments", "")
        )
    
    def verify_problem(
        self,
        correctness: int,
        clarity: int,
        difficulty_match: int,
        completeness: int,
        status: str,
        comments: str
    ) -> str:
        """
        验证当前题目
        
        Args:
            correctness: 正确性评分 (1-5)
            clarity: 清晰度评分 (1-5)
            difficulty_match: 难度匹配评分 (1-5)
            completeness: 完整性评分 (1-5)
            status: 验证状态 (approved/rejected/needs_revision)
            comments: 评论
        
        Returns:
            验证结果消息
        """
        if not self.problems:
            return "❌ 无题目可验证"
        
        problem = self.problems[self.current_index]
        problem_id = problem.get("id", "unknown")
        
        # 保存验证结果
        self.verifications[problem_id] = {
            "problem_id": problem_id,
            "scores": {
                "correctness": correctness,
                "clarity": clarity,
                "difficulty_match": difficulty_match,
                "completeness": completeness
            },
            "total_score": (correctness + clarity + difficulty_match + completeness) / 4,
            "status": status,
            "comments": comments,
            "verified_at": datetime.now().isoformat()
        }
        
        self._save_verifications()
        
        return f"✅ 题目 {problem_id} 验证完成！\n总分: {self.verifications[problem_id]['total_score']:.2f}/5.0"
    
    def next_problem(self) -> Tuple[str, str, str, str, str, str]:
        """下一个题目"""
        if self.current_index < len(self.problems) - 1:
            self.current_index += 1
        return self.get_current_problem()
    
    def prev_problem(self) -> Tuple[str, str, str, str, str, str]:
        """上一个题目"""
        if self.current_index > 0:
            self.current_index -= 1
        return self.get_current_problem()
    
    def get_statistics(self) -> str:
        """获取验证统计信息"""
        if not self.verifications:
            return "暂无验证数据"
        
        total = len(self.problems)
        verified = len(self.verifications)
        
        approved = sum(1 for v in self.verifications.values() if v["status"] == "approved")
        rejected = sum(1 for v in self.verifications.values() if v["status"] == "rejected")
        needs_revision = sum(1 for v in self.verifications.values() if v["status"] == "needs_revision")
        
        avg_score = sum(v["total_score"] for v in self.verifications.values()) / verified if verified > 0 else 0
        
        return f"""
📊 验证统计

总题目数: {total}
已验证: {verified} ({verified/total*100:.1f}%)
未验证: {total - verified}

验证结果:
- ✅ 通过: {approved}
- ❌ 拒绝: {rejected}
- 🔄 需修改: {needs_revision}

平均评分: {avg_score:.2f}/5.0
"""
    
    def launch(self, share: bool = False):
        """启动Gradio界面"""
        with gr.Blocks(title="AIME题目人工验证") as demo:
            gr.Markdown("# 🎯 AIME题目人工验证系统")
            gr.Markdown(f"数据文件: `{self.data_path}`")
            
            with gr.Row():
                with gr.Column(scale=2):
                    # 题目显示区域
                    title = gr.Textbox(label="当前题目", interactive=False)
                    problem_text = gr.Textbox(label="问题描述", lines=5, interactive=False)
                    answer_text = gr.Textbox(label="答案", interactive=False)
                    solution_text = gr.Textbox(label="解答过程", lines=10, interactive=False)
                    metadata_text = gr.Textbox(label="元数据", interactive=False)
                
                with gr.Column(scale=1):
                    # 评分区域
                    gr.Markdown("### 📝 评分 (1-5分)")
                    correctness_slider = gr.Slider(1, 5, value=3, step=1, label="正确性")
                    clarity_slider = gr.Slider(1, 5, value=3, step=1, label="清晰度")
                    difficulty_slider = gr.Slider(1, 5, value=3, step=1, label="难度匹配")
                    completeness_slider = gr.Slider(1, 5, value=3, step=1, label="完整性")
                    
                    # 状态选择
                    gr.Markdown("### ✅ 验证状态")
                    status_radio = gr.Radio(
                        choices=["approved", "rejected", "needs_revision"],
                        value="approved",
                        label="状态"
                    )
                    
                    # 评论
                    comments_text = gr.Textbox(label="评论", lines=3, placeholder="请输入评论...")
                    
                    # 验证按钮
                    verify_btn = gr.Button("✅ 提交验证", variant="primary")
                    verify_result = gr.Textbox(label="验证结果", interactive=False)
            
            # 导航按钮
            with gr.Row():
                prev_btn = gr.Button("⬅️ 上一题")
                next_btn = gr.Button("下一题 ➡️")
            
            # 统计信息
            with gr.Row():
                stats_text = gr.Textbox(label="验证统计", lines=10, interactive=False)
                refresh_stats_btn = gr.Button("🔄 刷新统计")
            
            # 加载初始题目
            demo.load(
                fn=self.get_current_problem,
                outputs=[title, problem_text, answer_text, solution_text, metadata_text, comments_text]
            )
            
            # 绑定事件
            verify_btn.click(
                fn=self.verify_problem,
                inputs=[correctness_slider, clarity_slider, difficulty_slider, completeness_slider, status_radio, comments_text],
                outputs=verify_result
            )
            
            next_btn.click(
                fn=self.next_problem,
                outputs=[title, problem_text, answer_text, solution_text, metadata_text, comments_text]
            )
            
            prev_btn.click(
                fn=self.prev_problem,
                outputs=[title, problem_text, answer_text, solution_text, metadata_text, comments_text]
            )
            
            refresh_stats_btn.click(
                fn=self.get_statistics,
                outputs=stats_text
            )
        
        demo.launch(share=share, server_name="127.0.0.1", server_port=7860)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python human_verification_ui.py <data_path>")
        print("示例: python human_verification_ui.py generated_data/aime_generated_20250110_120000.json")
        sys.exit(1)
    
    data_path = sys.argv[1]
    
    ui = HumanVerificationUI(data_path)
    ui.launch(share=False)

