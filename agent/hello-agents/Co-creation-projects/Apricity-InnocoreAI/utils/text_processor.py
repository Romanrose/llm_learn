"""
InnoCore AI 文本处理工具
"""

import re
from typing import List, Dict, Optional, Any, Tuple
import string
from collections import Counter
import asyncio

class TextProcessor:
    """文本处理器"""
    
    def __init__(self):
        self.stop_words = self._load_stop_words()
        self.punctuation = string.punctuation
    
    def _load_stop_words(self) -> set:
        """加载停用词"""
        # 简化的停用词列表
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
            'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours',
            'hers', 'ours', 'theirs', 'what', 'which', 'who', 'whom', 'whose',
            'where', 'when', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
            'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now', 'also'
        }
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符（保留基本标点）
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\\]', ' ', text)
        
        # 移除多余的空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """分词"""
        if not text:
            return []
        
        # 转换为小写并分词
        words = text.lower().split()
        
        # 移除标点符号
        words = [word.strip(self.punctuation) for word in words]
        
        # 过滤空字符串
        words = [word for word in words if word]
        
        return words
    
    def remove_stop_words(self, words: List[str]) -> List[str]:
        """移除停用词"""
        return [word for word in words if word not in self.stop_words]
    
    def extract_sentences(self, text: str) -> List[str]:
        """提取句子"""
        if not text:
            return []
        
        # 使用正则表达式分割句子
        sentences = re.split(r'[.!?]+', text)
        
        # 清理和过滤
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def extract_paragraphs(self, text: str) -> List[str]:
        """提取段落"""
        if not text:
            return []
        
        # 按双换行分割段落
        paragraphs = re.split(r'\n\s*\n', text)
        
        # 清理和过滤
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return paragraphs
    
    def calculate_readability(self, text: str) -> Dict[str, float]:
        """计算文本可读性指标"""
        if not text:
            return {"flesch_score": 0.0, "avg_sentence_length": 0.0, "avg_word_length": 0.0}
        
        sentences = self.extract_sentences(text)
        words = self.tokenize(text)
        
        if not sentences or not words:
            return {"flesch_score": 0.0, "avg_sentence_length": 0.0, "avg_word_length": 0.0}
        
        # 平均句子长度
        avg_sentence_length = len(words) / len(sentences)
        
        # 平均词长
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # 简化的Flesch Reading Ease分数
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length)
        
        return {
            "flesch_score": max(0, min(100, flesch_score)),
            "avg_sentence_length": avg_sentence_length,
            "avg_word_length": avg_word_length
        }
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """提取关键短语"""
        if not text:
            return []
        
        # 简化的关键短语提取
        words = self.tokenize(text)
        words = self.remove_stop_words(words)
        
        # 寻找常见的学术短语模式
        phrase_patterns = [
            r'\b\w+\s+\w+\b',  # 两词短语
            r'\b\w+\s+\w+\s+\w+\b',  # 三词短语
        ]
        
        phrases = []
        for pattern in phrase_patterns:
            matches = re.findall(pattern, text.lower())
            phrases.extend(matches)
        
        # 计算短语频率
        phrase_freq = Counter(phrases)
        
        # 过滤和排序
        filtered_phrases = [
            phrase for phrase, freq in phrase_freq.items()
            if freq > 1 and len(phrase.split()) >= 2
        ]
        
        filtered_phrases.sort(key=lambda x: phrase_freq[x], reverse=True)
        
        return filtered_phrases[:max_phrases]
    
    def detect_language(self, text: str) -> str:
        """检测语言（简化实现）"""
        if not text:
            return "unknown"
        
        # 简单的语言检测基于常见词汇
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        total_chars = chinese_chars + english_chars
        
        if total_chars == 0:
            return "unknown"
        
        chinese_ratio = chinese_chars / total_chars
        
        if chinese_ratio > 0.3:
            return "chinese"
        elif english_chars > 0:
            return "english"
        else:
            return "unknown"
    
    def extract_citations(self, text: str) -> List[Dict[str, Any]]:
        """提取引用"""
        citations = []
        
        # 数字引用模式 [1], [2-3]
        numeric_pattern = r'\[(\d+(?:-\d+)?)\]'
        numeric_matches = re.finditer(numeric_pattern, text)
        for match in numeric_matches:
            citations.append({
                "type": "numeric",
                "text": match.group(0),
                "reference": match.group(1),
                "position": match.start()
            })
        
        # 作者年份引用 (Smith, 2020)
        author_year_pattern = r'\(([A-Za-z]+(?:\s+et\s+al\.)?,\s*\d{4})\)'
        author_year_matches = re.finditer(author_year_pattern, text)
        for match in author_year_matches:
            citations.append({
                "type": "author_year",
                "text": match.group(0),
                "reference": match.group(1),
                "position": match.start()
            })
        
        return citations
    
    def extract_numbers_and_units(self, text: str) -> List[Dict[str, Any]]:
        """提取数字和单位"""
        patterns = [
            r'(\d+(?:\.\d+)?)\s*([a-zA-Z%]+)',  # 数字 + 单位
            r'(\d+(?:,\d{3})*(?:\.\d+)?)',  # 带逗号的数字
        ]
        
        results = []
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                results.append({
                    "text": match.group(0),
                    "number": match.group(1),
                    "unit": match.group(2) if len(match.groups()) > 1 else "",
                    "position": match.start()
                })
        
        return results
    
    def extract_acronyms(self, text: str) -> Dict[str, str]:
        """提取缩写词"""
        acronyms = {}
        
        # 查找全称(缩写)模式
        acronym_pattern = r'([A-Za-z\s]+)\s*\(([A-Z]{2,})\)'
        matches = re.finditer(acronym_pattern, text)
        
        for match in matches:
            full_name = match.group(1).strip()
            acronym = match.group(2)
            
            # 验证缩写是否来自全称的首字母
            initials = ''.join([word[0].upper() for word in full_name.split() if word])
            
            if acronym.startswith(initials):
                acronyms[acronym] = full_name
        
        return acronyms
    
    def summarize_text(self, text: str, max_sentences: int = 3) -> str:
        """文本摘要（简化实现）"""
        if not text:
            return ""
        
        sentences = self.extract_sentences(text)
        
        if len(sentences) <= max_sentences:
            return " ".join(sentences)
        
        # 简单的摘要算法：选择包含关键词最多的句子
        words = self.tokenize(text)
        words = self.remove_stop_words(words)
        word_freq = Counter(words)
        
        sentence_scores = []
        for sentence in sentences:
            sentence_words = self.tokenize(sentence)
            sentence_words = self.remove_stop_words(sentence_words)
            
            score = sum(word_freq.get(word, 0) for word in sentence_words)
            sentence_scores.append((sentence, score))
        
        # 选择得分最高的句子
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [sentence for sentence, score in sentence_scores[:max_sentences]]
        
        # 按原文顺序排列
        summary_sentences = []
        for sentence in sentences:
            if sentence in top_sentences:
                summary_sentences.append(sentence)
        
        return " ".join(summary_sentences)
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """实体提取（简化实现）"""
        entities = {
            "persons": [],
            "organizations": [],
            "locations": [],
            "dates": [],
            "numbers": []
        }
        
        # 人名模式（简化）
        person_pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        person_matches = re.findall(person_pattern, text)
        entities["persons"] = list(set(person_matches))
        
        # 组织模式（简化）
        org_patterns = [
            r'\b([A-Z][a-z]+\s+(?:University|Institute|Laboratory|Company|Corp|Inc|Ltd))\b',
            r'\b((?:[A-Z]+\s*){2,})\b'
        ]
        for pattern in org_patterns:
            matches = re.findall(pattern, text)
            entities["organizations"].extend(matches)
        entities["organizations"] = list(set(entities["organizations"]))
        
        # 日期模式
        date_patterns = [
            r'\b(\d{4})\b',
            r'\b(\d{1,2}/\d{1,2}/\d{4})\b',
            r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b'
        ]
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            entities["dates"].extend(matches)
        entities["dates"] = list(set(entities["dates"]))
        
        # 数字模式
        number_pattern = r'\b(\d+(?:\.\d+)?)\b'
        number_matches = re.findall(number_pattern, text)
        entities["numbers"] = list(set(number_matches))
        
        return entities
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（基于词汇重叠）"""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(self.tokenize(text1))
        words2 = set(self.tokenize(text2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    async def process_batch(self, texts: List[str], operations: List[str]) -> List[Dict[str, Any]]:
        """批量处理文本"""
        results = []
        
        for text in texts:
            result = {"text": text}
            
            for operation in operations:
                if operation == "clean":
                    result["cleaned"] = self.clean_text(text)
                elif operation == "tokenize":
                    result["tokens"] = self.tokenize(text)
                elif operation == "sentences":
                    result["sentences"] = self.extract_sentences(text)
                elif operation == "paragraphs":
                    result["paragraphs"] = self.extract_paragraphs(text)
                elif operation == "readability":
                    result["readability"] = self.calculate_readability(text)
                elif operation == "key_phrases":
                    result["key_phrases"] = self.extract_key_phrases(text)
                elif operation == "language":
                    result["language"] = self.detect_language(text)
                elif operation == "citations":
                    result["citations"] = self.extract_citations(text)
                elif operation == "entities":
                    result["entities"] = self.extract_entities(text)
                elif operation == "summary":
                    result["summary"] = self.summarize_text(text)
            
            results.append(result)
        
        return results