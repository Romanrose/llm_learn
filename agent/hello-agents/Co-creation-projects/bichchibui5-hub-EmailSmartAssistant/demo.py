#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能邮件助手 - 演示版本
EmailSmartAssistant - Demo Version

无需配置真实邮箱，直接体验所有功能
"""

import json
import re
from datetime import datetime, timedelta
from collections import Counter

class EmailDemo:
    def __init__(self):
        self.demo_emails = [
            {
                'id': '1',
                'subject': '紧急：项目进度汇报会议安排',
                'sender': 'manager@company.com',
                'date': '2024-01-15 09:00:00',
                'body': '各位同事，请准备明天下午2点的项目进度汇报会议。需要准备本周工作总结和下周计划。截止时间：2024-01-16 14:00。请确认参会。'
            },
            {
                'id': '2', 
                'subject': '客户咨询：产品功能详情',
                'sender': 'customer@client.com',
                'date': '2024-01-15 10:30:00',
                'body': '您好，我对贵公司的产品很感兴趣，希望了解更多功能详情。请问可以安排一次产品演示吗？我的联系方式：13800138000。期待您的回复。'
            },
            {
                'id': '3',
                'subject': '系统维护通知',
                'sender': 'noreply@system.com', 
                'date': '2024-01-15 11:00:00',
                'body': '系统将于2024-01-20 02:00-04:00进行维护升级，期间服务可能中断。请提前做好准备工作。如有疑问请联系技术支持。'
            },
            {
                'id': '4',
                'subject': '限时优惠！立即购买享受8折优惠',
                'sender': 'promotion@ads.com',
                'date': '2024-01-15 12:00:00',
                'body': '亲爱的用户，我们的产品正在进行限时促销活动！现在购买可享受8折优惠，机会难得，不要错过！点击链接立即购买。'
            },
            {
                'id': '5',
                'subject': '个人：周末聚餐安排',
                'sender': 'friend@personal.com',
                'date': '2024-01-15 13:00:00',
                'body': '嗨！这个周末我们一起聚餐吧，时间定在周六晚上7点，地点在市中心的那家川菜馆。请确认是否能参加，我好提前订位。'
            },
            {
                'id': '6',
                'subject': 'Urgent: Meeting Request',
                'sender': 'boss@company.com',
                'date': '2024-01-15 14:00:00',
                'body': 'Hi team, we need to schedule an urgent meeting tomorrow at 3 PM to discuss the quarterly results. Please prepare your reports and confirm attendance by 5 PM today.'
            }
        ]
        
        self.classification_rules = {
            'work_keywords': ['会议', '项目', '工作', '任务', '汇报', 'meeting', 'project', 'work', 'task', 'urgent'],
            'customer_keywords': ['客户', '咨询', '购买', '服务', 'customer', 'inquiry', 'purchase', 'service'],
            'personal_keywords': ['个人', '家庭', '朋友', 'personal', 'family', 'friend', '聚餐'],
            'spam_keywords': ['广告', '推广', '营销', '优惠', 'advertisement', 'promotion', 'marketing', '折扣']
        }
        
        self.reply_templates = {
            'work': {
                'zh': '感谢您的邮件。关于{subject}，我已收到您的信息。我将在24小时内回复您详细的反馈。如有紧急事项，请随时联系我。\n\n此致\n敬礼',
                'en': 'Thank you for your email regarding {subject}. I have received your information and will provide detailed feedback within 24 hours. Please feel free to contact me if there are any urgent matters.\n\nBest regards'
            },
            'customer': {
                'zh': '尊敬的客户，\n\n感谢您对我们产品/服务的关注。关于您咨询的{subject}，我们将安排专业人员在24小时内为您提供详细解答。\n\n如有其他问题，欢迎随时联系我们。\n\n此致\n敬礼',
                'en': 'Dear Valued Customer,\n\nThank you for your interest in our products/services. Regarding your inquiry about {subject}, we will arrange for a professional to provide you with detailed answers within 24 hours.\n\nPlease feel free to contact us if you have any other questions.\n\nBest regards'
            },
            'general': {
                'zh': '您好，\n\n已收到您的邮件，我将仔细阅读并在24小时内回复。\n\n谢谢！',
                'en': 'Hello,\n\nI have received your email and will read it carefully and reply within 24 hours.\n\nThank you!'
            }
        }

    def classify_email(self, email):
        """邮件分类"""
        subject = email['subject'].lower()
        body = email['body'].lower()
        sender = email['sender'].lower()
        
        text_content = f"{subject} {body}"
        
        # 检查垃圾邮件
        spam_score = sum(1 for keyword in self.classification_rules['spam_keywords'] 
                        if keyword in text_content)
        if spam_score >= 2:
            return {'type': 'spam', 'priority': 'low', 'sender_type': 'external'}
        
        # 检查工作邮件
        work_score = sum(1 for keyword in self.classification_rules['work_keywords'] 
                        if keyword in text_content)
        
        # 检查客户邮件
        customer_score = sum(1 for keyword in self.classification_rules['customer_keywords'] 
                           if keyword in text_content)
        
        # 检查个人邮件
        personal_score = sum(1 for keyword in self.classification_rules['personal_keywords'] 
                           if keyword in text_content)
        
        # 确定类型
        scores = {'work': work_score, 'customer': customer_score, 'personal': personal_score}
        email_type = max(scores, key=scores.get) if max(scores.values()) > 0 else 'other'
        
        # 确定优先级
        priority = 'high' if any(word in text_content for word in ['紧急', 'urgent', 'asap', '重要']) else 'medium'
        if email_type == 'spam':
            priority = 'low'
        
        # 确定发件人类型
        if 'company.com' in sender:
            sender_type = 'colleague'
        elif 'noreply' in sender or 'no-reply' in sender:
            sender_type = 'system'
        elif email_type == 'customer':
            sender_type = 'customer'
        else:
            sender_type = 'external'
        
        return {
            'type': email_type,
            'priority': priority,
            'sender_type': sender_type
        }

    def extract_info(self, email):
        """提取关键信息"""
        body = email['body']
        
        # 提取日期
        date_patterns = [
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}月\d{1,2}日',
            r'\d{1,2}/\d{1,2}'
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, body))
        
        # 提取时间
        time_patterns = [
            r'\d{1,2}:\d{2}',
            r'\d{1,2}点',
            r'\d{1,2} PM',
            r'\d{1,2} AM'
        ]
        
        times = []
        for pattern in time_patterns:
            times.extend(re.findall(pattern, body))
        
        # 提取联系方式
        phones = re.findall(r'1[3-9]\d{9}', body)
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', body)
        
        # 提取待办事项（包含关键词的句子）
        todo_keywords = ['需要', '请', '准备', 'need', 'please', 'prepare', '确认']
        sentences = body.replace('。', '.').split('.')
        todos = []
        for sentence in sentences:
            if any(keyword in sentence for keyword in todo_keywords):
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 5:
                    todos.append(clean_sentence)
        
        return {
            'dates': dates,
            'times': times,
            'phones': phones,
            'emails': emails,
            'todos': todos[:3]  # 最多3个
        }

    def generate_reply(self, email, classification):
        """生成回复草稿"""
        if classification['type'] == 'spam':
            return None
        
        # 检测语言
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in email['body'])
        lang = 'zh' if is_chinese else 'en'
        
        # 选择模板
        template_type = classification['type'] if classification['type'] in ['work', 'customer'] else 'general'
        template = self.reply_templates[template_type][lang]
        
        # 生成回复
        reply_content = template.format(subject=email['subject'])
        
        return {
            'to': email['sender'],
            'subject': f"Re: {email['subject']}",
            'content': reply_content,
            'language': lang,
            'template_type': template_type
        }

    def run_demo(self):
        """运行演示"""
        print("🤖 智能邮件助手 - 演示版本")
        print("=" * 50)
        print(f"📧 演示邮件数量: {len(self.demo_emails)}")
        print()
        
        results = []
        stats = {'total': 0, 'classified': 0, 'replies': 0, 'reminders': 0}
        
        for i, email in enumerate(self.demo_emails, 1):
            print(f"处理邮件 {i}/{len(self.demo_emails)}: {email['subject'][:30]}...")
            
            # 分类
            classification = self.classify_email(email)
            stats['classified'] += 1
            
            # 信息提取
            extracted_info = self.extract_info(email)
            
            # 生成回复
            reply = self.generate_reply(email, classification)
            if reply:
                stats['replies'] += 1
            
            # 创建提醒
            reminders = len(extracted_info['dates']) + len(extracted_info['todos'])
            stats['reminders'] += reminders
            
            results.append({
                'email': email,
                'classification': classification,
                'extracted_info': extracted_info,
                'reply': reply,
                'reminders_count': reminders
            })
        
        stats['total'] = len(self.demo_emails)
        
        print("\n✅ 处理完成！")
        self.display_results(results, stats)

    def display_results(self, results, stats):
        """显示结果"""
        print("\n📊 处理统计:")
        print(f"  总邮件数: {stats['total']}")
        print(f"  已分类: {stats['classified']}")
        print(f"  生成回复: {stats['replies']}")
        print(f"  创建提醒: {stats['reminders']}")
        
        # 分类统计
        types = [r['classification']['type'] for r in results]
        priorities = [r['classification']['priority'] for r in results]
        
        print("\n📋 分类统计:")
        type_counts = Counter(types)
        for email_type, count in type_counts.items():
            print(f"  {email_type}: {count}")
        
        print("\n⚡ 优先级统计:")
        priority_counts = Counter(priorities)
        for priority, count in priority_counts.items():
            print(f"  {priority}: {count}")
        
        print("\n📝 处理结果样例:")
        print("-" * 50)
        
        for i, result in enumerate(results[:3], 1):  # 显示前3个
            email = result['email']
            classification = result['classification']
            extracted = result['extracted_info']
            reply = result['reply']
            
            print(f"\n邮件 {i}:")
            print(f"  主题: {email['subject']}")
            print(f"  发件人: {email['sender']}")
            print(f"  分类: {classification['type']} | 优先级: {classification['priority']}")
            
            if extracted['dates']:
                print(f"  关键日期: {', '.join(extracted['dates'])}")
            if extracted['times']:
                print(f"  时间: {', '.join(extracted['times'])}")
            if extracted['todos']:
                print(f"  待办: {extracted['todos'][0][:50]}...")
            
            if reply:
                print(f"  回复草稿 ({reply['language']}): {reply['content'][:80]}...")
            
            print(f"  提醒数量: {result['reminders_count']}")
        
        print("\n🎉 演示完成！")
        print("\n💡 下一步:")
        print("1. 查看完整功能请运行: jupyter notebook EmailSmartAssistant.ipynb")
        print("2. 配置真实邮箱请编辑: config/email_config.json")
        print("3. 安装完整依赖请运行: pip install -r requirements.txt")

if __name__ == "__main__":
    demo = EmailDemo()
    demo.run_demo()