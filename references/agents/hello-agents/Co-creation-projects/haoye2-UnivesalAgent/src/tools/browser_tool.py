import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
import time
import re
import html

class BrowserTool:
    name = "browser_search"
    description = "执行网页搜索（支持多种搜索引擎和内容提取）"
    
    def get_parameters(self):
        return {
            "input": {"type": "str", "description": "搜索关键词", "required": True}
        }

    def _is_valid_result(self, title, url):
        """验证搜索结果的有效性"""
        if not title or len(title.strip()) < 3:
            return False
        
        # 过滤导航链接和无意义内容
        skip_keywords = [
            "next", "previous", "more", "about", "help", "settings",
            "privacy", "terms", "feedback", "donate", "install",
            "download", "login", "register", "sign in", "sign up"
        ]
        
        title_lower = title.lower()
        if any(keyword in title_lower for keyword in skip_keywords):
            return False
        
        # 过滤广告和推广链接
        ad_indicators = ["ad", "sponsored", "promotion", "广告", "推广"]
        if any(indicator in title_lower for indicator in ad_indicators):
            return False
        
        return True

    def _clean_text(self, text):
        """清理文本内容"""
        if not text:
            return ""
        
        # 移除多余空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()[\]{}"\'-]', '', text)
        
        return text[:200]  # 限制长度

    def _search_searx(self, query, limit=5):
        """使用多个搜索引擎实例 - 稳定版，优先支持中文搜索"""
        # 精选多个稳定的搜索引擎，优先支持中文
        search_instances = [
            {
                "name": "Searx.xyz",
                "url": "https://searx.xyz/search",
                "timeout": 10,
                "type": "searx"
            },
            {
                "name": "Searx.be",
                "url": "https://searx.be/search",
                "timeout": 10,
                "type": "searx"
            },
            {
                "name": "Brave搜索",
                "url": "https://search.brave.com/search",
                "timeout": 8,
                "type": "brave"
            },
            {
                "name": "Ecosia",
                "url": "https://www.ecosia.org/search",
                "timeout": 8,
                "type": "ecosia"
            },
            {
                "name": "Qwant",
                "url": "https://www.qwant.com",
                "timeout": 8,
                "type": "qwant"
            }
        ]
        
        for instance in search_instances:
            try:
                print(f"🔍 尝试 {instance['name']}...")
                result = self._try_search_instance(instance, query, limit)
                if result and len(result) > 0:
                    print(f"✅ {instance['name']} 搜索成功，找到 {len(result)} 个结果")
                    return result, True
                    
            except Exception as e:
                print(f"⚠️ {instance['name']} 失败: {str(e)[:50]}")
                continue  # 静默失败，快速切换
        
        # 快速降级到搜索建议
        print("🔗 所有搜索引擎失败，提供搜索建议")
        return self._get_search_suggestions(query), True

    def _try_search_instance(self, instance, query, limit):
        """尝试单个搜索引擎实例"""
        if instance['type'] == 'searx':
            return self._try_searx_instance(instance, query, limit)
        elif instance['type'] == 'duckduckgo':
            return self._try_duckduckgo_instance(instance, query, limit)
        elif instance['type'] == 'startpage':
            return self._try_startpage_instance(instance, query, limit)
        elif instance['type'] == 'qwant':
            return self._try_qwant_instance(instance, query, limit)
        elif instance['type'] == 'brave':
            return self._try_brave_instance(instance, query, limit)
        elif instance['type'] == 'ecosia':
            return self._try_ecosia_instance(instance, query, limit)
        else:
            return None

    def _try_searx_instance(self, instance, query, limit):
        """尝试Searx实例 - 优化中文搜索支持"""
        # 检测是否为中文查询
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in query)
        
        params = {
            'q': query,
            'format': 'json',
            'engines': 'google,bing,duckduckgo,yandex' if not is_chinese else 'google,bing,yandex,baidu',
            'language': 'zh-CN' if is_chinese else 'auto'
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8" if is_chinese else "en-US,en;q=0.9"
        }
        
        try:
            response = requests.get(
                instance['url'], 
                params=params, 
                headers=headers, 
                timeout=instance['timeout']
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results = []
                    
                    for item in data.get('results', [])[:limit]:
                        title = self._clean_text(item.get('title', ''))
                        url = item.get('url', '')
                        content = item.get('content', '')
                        
                        if self._is_valid_result(title, url):
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': self._clean_text(content)[:200],
                                'source': f"{instance['name']}/{item.get('engine', 'unknown')}"
                            })
                    
                    return results if results else None
                except Exception as e:
                    print(f"⚠️ 解析Searx响应失败: {str(e)[:50]}")
                    return None
            else:
                print(f"⚠️ Searx返回状态码: {response.status_code}")
                return None
        except requests.Timeout:
            print(f"⚠️ {instance['name']} 请求超时")
            return None
        except Exception as e:
            print(f"⚠️ {instance['name']} 请求异常: {str(e)[:50]}")
            return None

    def _try_duckduckgo_instance(self, instance, query, limit):
        """尝试DuckDuckGo实例"""
        params = {
            'q': query,
            'kl': 'cn-zh'
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        response = requests.get(
            instance['url'], 
            params=params, 
            headers=headers, 
            timeout=instance['timeout']
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extract_duckduckgo_results_from_soup(soup, limit)
        
        return None

    def _try_startpage_instance(self, instance, query, limit):
        """尝试Startpage实例"""
        params = {
            'query': query,
            'cat': 'web',
            'pl': 'ext-ff',
            'extVersion': '1.3.0'
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        response = requests.get(
            instance['url'], 
            params=params, 
            headers=headers, 
            timeout=instance['timeout']
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extract_startpage_results(soup, limit)
        
        return None

    def _try_qwant_instance(self, instance, query, limit):
        """尝试Qwant实例"""
        params = {
            'q': query,
            't': 'web',
            'locale': 'zh_CN'
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        response = requests.get(
            instance['url'], 
            params=params, 
            headers=headers, 
            timeout=instance['timeout']
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extract_qwant_results(soup, limit)
        
        return None

    def _try_brave_instance(self, instance, query, limit):
        """尝试Brave搜索实例"""
        params = {
            'q': query,
            'source': 'web'
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        
        try:
            response = requests.get(
                instance['url'], 
                params=params, 
                headers=headers, 
                timeout=instance['timeout']
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Brave搜索结果提取（需要根据实际HTML结构调整）
                results = []
                result_divs = soup.find_all('div', class_=['result', 'web-result'])
                
                for div in result_divs[:limit]:
                    title_elem = div.find('a') or div.find('h2')
                    snippet_elem = div.find('p') or div.find('span', class_='snippet')
                    
                    if title_elem:
                        title = self._clean_text(title_elem.get_text())
                        url = title_elem.get('href', '')
                        snippet = self._clean_text(snippet_elem.get_text()) if snippet_elem else ''
                        
                        if self._is_valid_result(title, url):
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet[:200],
                                'source': 'Brave'
                            })
                
                return results if results else None
        except Exception:
            return None
        
        return None

    def _try_ecosia_instance(self, instance, query, limit):
        """尝试Ecosia搜索实例"""
        params = {
            'q': query
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        
        try:
            response = requests.get(
                instance['url'], 
                params=params, 
                headers=headers, 
                timeout=instance['timeout']
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Ecosia搜索结果提取（需要根据实际HTML结构调整）
                results = []
                result_divs = soup.find_all('div', class_=['result', 'web-result', 'result__body'])
                
                for div in result_divs[:limit]:
                    title_elem = div.find('a') or div.find('h2')
                    snippet_elem = div.find('p') or div.find('span', class_='result__snippet')
                    
                    if title_elem:
                        title = self._clean_text(title_elem.get_text())
                        url = title_elem.get('href', '')
                        snippet = self._clean_text(snippet_elem.get_text()) if snippet_elem else ''
                        
                        if self._is_valid_result(title, url):
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet[:200],
                                'source': 'Ecosia'
                            })
                
                return results if results else None
        except Exception:
            return None
        
        return None

    def _extract_duckduckgo_results_from_soup(self, soup, limit):
        """从DuckDuckGo HTML中提取结果"""
        results = []
        
        # 查找搜索结果
        result_divs = soup.find_all('div', class_='result')
        
        for div in result_divs[:limit]:
            title_elem = div.find('a', class_='result__a')
            snippet_elem = div.find('a', class_='result__snippet')
            
            if title_elem:
                title = self._clean_text(title_elem.get_text())
                url = title_elem.get('href', '')
                snippet = self._clean_text(snippet_elem.get_text()) if snippet_elem else ''
                
                if self._is_valid_result(title, url):
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet[:200],
                        'source': 'DuckDuckGo'
                    })
        
        return results

    def _extract_startpage_results(self, soup, limit):
        """从Startpage HTML中提取结果"""
        results = []
        
        # 查找搜索结果
        result_divs = soup.find_all('div', class_='w-gl__result')
        
        for div in result_divs[:limit]:
            title_elem = div.find('h3')
            link_elem = title_elem.find('a') if title_elem else None
            snippet_elem = div.find('p', class_='w-gl__description')
            
            if link_elem:
                title = self._clean_text(link_elem.get_text())
                url = link_elem.get('href', '')
                snippet = self._clean_text(snippet_elem.get_text()) if snippet_elem else ''
                
                if self._is_valid_result(title, url):
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet[:200],
                        'source': 'Startpage'
                    })
        
        return results

    def _extract_qwant_results(self, soup, limit):
        """从Qwant HTML中提取结果"""
        results = []
        
        # 查找搜索结果
        result_divs = soup.find_all('div', class_='result')
        
        for div in result_divs[:limit]:
            title_elem = div.find('a', class_='result--web')
            snippet_elem = div.find('p', class_='result__desc')
            
            if title_elem:
                title = self._clean_text(title_elem.get_text())
                url = title_elem.get('href', '')
                snippet = self._clean_text(snippet_elem.get_text()) if snippet_elem else ''
                
                if self._is_valid_result(title, url):
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet[:200],
                        'source': 'Qwant'
                    })
        
        return results

    def _extract_duckduckgo_results(self, soup, limit=5):
        """提取DuckDuckGo搜索结果"""
        results = []
        
        # DuckDuckGo现在返回202状态码，需要JavaScript渲染
        # 我们尝试从HTML中提取任何有用的信息
        
        # 方法1：查找所有外部链接
        all_links = soup.find_all('a', href=True)
        external_links = []
        
        for link in all_links:
            href = link.get('href', '')
            title = self._clean_text(link.get_text(strip=True))
            
            # 过滤外部链接（非DuckDuckGo内部链接）
            if (href and 
                not href.startswith('javascript:') and
                not href.startswith('#') and
                'duckduckgo.com' not in href and
                len(title) > 3 and
                self._is_valid_result(title, href)):
                
                external_links.append({
                    'title': title,
                    'url': href,
                    'snippet': '',
                    'link_element': link
                })
        
        # 方法2：如果外部链接不够，尝试从页面文本中提取信息
        if len(external_links) < 2:
            print("⚠️ 外部链接较少，尝试文本提取")
            
            # 查找页面中的主要文本内容
            text_content = soup.get_text()
            
            # 尝试提取URL模式
            import re
            url_pattern = r'https?://[^\s<>"\'()]+'
            urls = re.findall(url_pattern, text_content)
            
            for url in urls[:limit]:
                # 从URL中提取可能的标题
                domain = url.split('/')[2] if '/' in url else url
                title = domain.replace('www.', '').title()
                
                if self._is_valid_result(title, url):
                    external_links.append({
                        'title': title,
                        'url': url,
                        'snippet': f'来自 {domain}',
                        'link_element': None
                    })
        
        # 方法3：如果还是没有足够结果，提供搜索建议
        if len(external_links) < 2:
            print("⚠️ 搜索结果有限，提供搜索建议")
            
            suggestions = [
                {
                    'title': f'在Google搜索 "{self.last_query}"',
                    'url': f'https://www.google.com/search?q={self.last_query}',
                    'snippet': '使用Google搜索引擎',
                    'link_element': None
                },
                {
                    'title': f'在Bing搜索 "{self.last_query}"',
                    'url': f'https://www.bing.com/search?q={self.last_query}',
                    'snippet': '使用Bing搜索引擎',
                    'link_element': None
                }
            ]
            external_links.extend(suggestions)
        
        # 去重并限制结果数量
        seen_urls = set()
        unique_results = []
        
        for result in external_links:
            if result['url'] and result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
                if len(unique_results) >= limit:
                    break
        
        return unique_results

    def _extract_content_from_url(self, url, max_length=300):
        """从URL提取主要内容"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return "内容获取失败"
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除脚本和样式标签
            for script in soup(["script", "style", "nav", "footer", "header", "aside", "advertisement"]):
                script.decompose()
            
            # 智能内容提取策略
            content = self._extract_main_content(soup)
            
            if not content:
                content = soup.get_text(strip=True)
            
            # 清理和优化内容
            content = self._clean_and_format_content(content)
            
            return content[:max_length] + "..." if len(content) > max_length else content
            
        except Exception as e:
            return f"内容提取失败: {str(e)[:50]}"

    def _extract_main_content(self, soup):
        """智能提取页面主要内容"""
        # 优先级策略：从最具体到最通用
        extraction_strategies = [
            # 1. 文章相关标签
            ['article', 'main article', '.article-content', '.post-content'],
            # 2. 主要内容区域
            ['main', '.main', '.content', '.main-content'],
            # 3. 常见内容类名
            ['.entry-content', '.post-body', '.article-body', '.content-area'],
            # 4. 通用容器
            ['.container', '.wrapper', '.page-content'],
            # 5. 最后尝试body
            ['body']
        ]
        
        for strategy in extraction_strategies:
            for selector in strategy:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    # 验证内容质量
                    if self._is_quality_content(content):
                        return content
        
        return ""

    def _is_quality_content(self, content):
        """验证内容质量"""
        if not content or len(content) < 50:
            return False
        
        # 过滤导航和菜单内容
        nav_keywords = ['导航', '菜单', '首页', '登录', '注册', '搜索', '联系', '关于', 'privacy', 'terms', 'home', 'login', 'register', 'contact', 'about']
        content_lower = content.lower()
        
        for keyword in nav_keywords:
            if keyword in content_lower:
                return False
        
        # 检查是否包含有意义的句子
        sentences = content.split('。')
        meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        return len(meaningful_sentences) >= 2

    def _clean_and_format_content(self, content):
        """清理和格式化内容"""
        if not content:
            return ""
        
        # 移除多余空白
        content = re.sub(r'\s+', ' ', content.strip())
        
        # 移除特殊字符，保留中文标点
        content = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()[\]{}"\'。，！？：；（）【】""''-]', '', content)
        
        # 移除重复的换行和空格
        content = re.sub(r'\n\s*\n', '\n', content)
        content = re.sub(r' {2,}', ' ', content)
        
        # 提取前几个有意义的句子
        sentences = re.split(r'[。！？.!?]', content)
        meaningful_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and len(sentence) < 100:  # 合理的句子长度
                meaningful_sentences.append(sentence)
                if len(meaningful_sentences) >= 3:  # 最多3个句子
                    break
        
        return '。'.join(meaningful_sentences)

    def _enhance_search_results(self, results, limit=3):
        """增强搜索结果，提取内容预览"""
        enhanced_results = []
        
        for i, result in enumerate(results):
            if i >= limit:  # 只增强前几个结果
                break
            
            if result['url'] and result['url'].startswith('http'):
                print(f"📄 提取内容: {result['title'][:30]}...")
                content = self._extract_content_from_url(result['url'])
                result['snippet'] = content
                result['enhanced'] = True
            else:
                result['enhanced'] = False
            
            enhanced_results.append(result)
        
        # 添加未增强的结果
        enhanced_results.extend(results[limit:])
        
        return enhanced_results

    def _fallback_extraction(self, soup, limit=5):
        """备用结果提取方法"""
        results = []
        
        # 方法1：提取标题元素
        for tag in ["h1", "h2", "h3", "h4"]:
            elements = soup.find_all(tag)
            for elem in elements:
                if len(results) >= limit:
                    break
                    
                title = self._clean_text(elem.get_text(strip=True))
                if self._is_valid_result(title, ""):
                    results.append({
                        "title": title,
                        "url": "",
                        "snippet": ""
                    })
        
        # 方法2：提取文本块
        if not results:
            text_blocks = soup.get_text().split('\n')
            for block in text_blocks:
                if len(results) >= limit:
                    break
                    
                block = self._clean_text(block)
                if len(block) > 20 and len(block) < 150:
                    results.append({
                        "title": block,
                        "url": "",
                        "snippet": ""
                    })
        
        return results

    def run(self, parameters):
        # 确保参数处理的安全性
        if isinstance(parameters, dict):
            query = parameters.get("input", "")
        else:
            query = str(parameters) if parameters else ""

        # 参数验证
        if not query or not query.strip():
            return "错误：搜索关键词不能为空"
        
        query = query.strip()
        self.last_query = query  # 保存查询用于建议
        limit = 5  # 增加结果数量
        
        # URL 编码查询参数
        encoded_query = quote_plus(query)
        url = f"https://duckduckgo.com/html/?q={encoded_query}"
        
        # 使用更真实的User-Agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # 检测是否为中文查询
        is_chinese = any('\u4e00' <= char <= '\u9fff' for char in query)
        
        # 对于中文搜索，直接使用Searx搜索引擎，跳过DuckDuckGo（避免202问题）
        if is_chinese:
            print(f"🌐 检测到中文查询，使用多引擎搜索策略...")
            searx_results, searx_success = self._search_searx(query, limit)
            
            if searx_success and searx_results:
                results = searx_results
                search_engine = "Searx多引擎"
                print(f"✅ 中文搜索成功，找到 {len(results)} 个结果")
            else:
                # 如果Searx失败，提供搜索建议
                print("⚠️ 所有搜索引擎失败，提供搜索建议")
                results = self._get_search_suggestions(query)
                search_engine = "搜索建议"
        else:
            # 英文搜索：先尝试DuckDuckGo，失败后使用Searx
            max_retries = 2  # 减少重试次数，快速切换到Searx
            duckduckgo_success = False
            
            for attempt in range(max_retries):
                try:
                    print(f"🔍 尝试DuckDuckGo搜索: {query} (尝试 {attempt + 1}/{max_retries})")
                    
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    # DuckDuckGo经常返回202，直接跳过
                    if response.status_code == 202:
                        print("⚠️ DuckDuckGo返回202（需要JavaScript），切换到Searx...")
                        break
                    
                    if response.status_code != 200:
                        if attempt < max_retries - 1:
                            time.sleep(1)
                            continue
                        break
                    
                    # 检查响应内容
                    if len(response.text) < 1000:
                        if attempt < max_retries - 1:
                            time.sleep(1)
                            continue
                        break
                    
                    soup = BeautifulSoup(response.text, "html.parser")
                    results = self._extract_duckduckgo_results(soup, limit)
                    
                    if results and len(results) > 0:
                        duckduckgo_success = True
                        search_engine = "DuckDuckGo"
                        print(f"✅ DuckDuckGo搜索成功，找到 {len(results)} 个结果")
                        break
                        
                except Exception as e:
                    print(f"⚠️ DuckDuckGo尝试失败: {str(e)[:50]}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    break
            
            # 如果DuckDuckGo失败，使用Searx
            if not duckduckgo_success:
                print("🌐 DuckDuckGo失败，切换到Searx搜索引擎...")
                searx_results, searx_success = self._search_searx(query, limit)
                
                if searx_success and searx_results:
                    results = searx_results
                    search_engine = "Searx多引擎"
                    print(f"✅ Searx搜索成功，找到 {len(results)} 个结果")
                else:
                    print("⚠️ 所有搜索引擎失败，提供搜索建议")
                    results = self._get_search_suggestions(query)
                    search_engine = "搜索建议"
        
        # 增强搜索结果（提取内容预览）
        if results:
            print("🚀 增强搜索结果，提取内容预览...")
            enhanced_results = self._enhance_search_results(results, limit=3)
            results = enhanced_results
        
        # 格式化输出结果
        if results:
            formatted_results = []
            for i, result in enumerate(results, 1):
                result_text = f"{i}. {result['title']}"
                
                if result['url']:
                    result_text += f"\n   🔗 {result['url']}"
                
                if result['snippet']:
                    # 如果是增强的结果，显示内容预览
                    if result.get('enhanced'):
                        result_text += f"\n   📄 内容预览: {result['snippet']}"
                    else:
                        result_text += f"\n   📝 {result['snippet']}"
                
                formatted_results.append(result_text)
            
            return "\n\n".join(formatted_results)
        else:
            return f"未找到关于 '{query}' 的搜索结果。请尝试使用不同的关键词。"
        
    def _get_search_suggestions(self, query):
        """快速提供搜索建议"""
        return [
            {
                'title': f'Google搜索: {query}',
                'url': f'https://www.google.com/search?q={query}',
                'snippet': '使用Google搜索引擎',
                'source': 'Google'
            },
            {
                'title': f'Bing搜索: {query}',
                'url': f'https://www.bing.com/search?q={query}',
                'snippet': '使用Bing搜索引擎',
                'source': 'Bing'
            }
        ]

        return "搜索失败，已多次重试。请稍后再试。"
