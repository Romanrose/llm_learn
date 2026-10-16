"""
引用校验API路由
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging
import httpx
import re

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic模型
class CitationValidationRequest(BaseModel):
    citation: str
    format: str = "bibtex"  # bibtex, apa, ieee, mla

class CitationGenerateRequest(BaseModel):
    doi: Optional[str] = None
    title: Optional[str] = None
    authors: Optional[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    format: str = "bibtex"

@router.post("/validate", response_model=Dict[str, Any])
async def validate_citation(request: CitationValidationRequest):
    """校验引用格式 - 支持 ArXiv、DOI 和 AI 辅助验证"""
    try:
        logger.info(f"校验引用: {request.citation[:100]}...")
        
        metadata = None
        verified = False
        doi = None
        
        # 1. 尝试识别 ArXiv URL 或 ID
        arxiv_pattern = r'(?:arxiv\.org/abs/|arXiv:)(\d+\.\d+)'
        arxiv_match = re.search(arxiv_pattern, request.citation, re.IGNORECASE)
        
        if arxiv_match:
            arxiv_id = arxiv_match.group(1)
            logger.info(f"找到 ArXiv ID: {arxiv_id}")
            
            try:
                import arxiv
                search = arxiv.Search(id_list=[arxiv_id])
                paper = next(search.results(), None)
                
                if paper:
                    metadata = {
                        'title': paper.title,
                        'authors': [author.name for author in paper.authors],
                        'year': paper.published.year,
                        'journal': 'arXiv preprint',
                        'arxiv_id': arxiv_id,
                        'url': paper.entry_id
                    }
                    verified = True
                    logger.info(f"ArXiv 论文信息获取成功: {metadata['title'][:50]}...")
                    logger.info(f"作者数量: {len(metadata['authors'])}")
                else:
                    logger.warning(f"未找到 ArXiv ID: {arxiv_id}")
            except Exception as e:
                logger.error(f"ArXiv 查询失败: {str(e)}", exc_info=True)
        
        # 2. 尝试从引用中提取 DOI
        if not verified:
            doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
            doi_match = re.search(doi_pattern, request.citation, re.IGNORECASE)
            
            if doi_match:
                doi = doi_match.group(0)
                logger.info(f"找到 DOI: {doi}")
                
                # 使用 Crossref API 验证 DOI
                async with httpx.AsyncClient() as client:
                    try:
                        response = await client.get(
                            f"https://api.crossref.org/works/{doi}",
                            timeout=10.0
                        )
                        if response.status_code == 200:
                            data = response.json()
                            msg = data.get('message', {})
                            metadata = {
                                'title': msg.get('title', [''])[0],
                                'authors': [f"{a.get('given', '')} {a.get('family', '')}" for a in msg.get('author', [])],
                                'year': msg.get('published', {}).get('date-parts', [[None]])[0][0],
                                'journal': msg.get('container-title', [''])[0],
                                'volume': msg.get('volume', ''),
                                'issue': msg.get('issue', ''),
                                'pages': msg.get('page', ''),
                                'doi': doi
                            }
                            verified = True
                            logger.info("DOI 验证成功")
                    except Exception as e:
                        logger.warning(f"DOI 验证失败: {str(e)}")
        
        # 3. 如果仍未验证，尝试使用 AI 解析引用信息
        if not verified:
            logger.info("尝试使用 AI 解析引用信息...")
            try:
                from core.config import get_config
                from core.llm_adapter import get_llm_adapter
                
                config = get_config()
                if config.llm.api_key:
                    llm = get_llm_adapter()
                    
                    prompt = f"""请从以下引用信息中提取关键元数据，并以 JSON 格式返回。

引用信息：
{request.citation}

请提取以下信息（如果有的话）：
- title: 论文标题
- authors: 作者列表（字符串数组，例如 ["Zhang San", "Li Si"]）
- year: 发表年份（数字）
- journal: 期刊或会议名称
- volume: 卷号
- issue: 期号
- pages: 页码
- doi: DOI（如果有）
- arxiv_id: ArXiv ID（如果有）

只返回纯 JSON 格式，不要任何其他文字说明。如果某个字段不存在，请省略该字段。

示例输出：
{{"title": "论文标题", "authors": ["作者1", "作者2"], "year": 2024, "journal": "期刊名"}}"""
                    
                    response = await llm.ainvoke(prompt)
                    ai_result = response.content if hasattr(response, 'content') else str(response)
                    
                    # 尝试解析 AI 返回的 JSON
                    import json
                    # 提取 JSON 部分（支持代码块格式）
                    json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', ai_result)
                    if json_match:
                        metadata = json.loads(json_match.group(1))
                        verified = True
                        logger.info("AI 解析成功（代码块格式）")
                    else:
                        json_match = re.search(r'\{[\s\S]*\}', ai_result)
                        if json_match:
                            metadata = json.loads(json_match.group(0))
                            verified = True
                            logger.info("AI 解析成功")
            except Exception as e:
                logger.warning(f"AI 解析失败: {str(e)}")
        
        # 生成标准格式的引用
        if metadata and verified:
            title = metadata.get('title', 'Unknown Title')
            authors = metadata.get('authors', []) if isinstance(metadata.get('authors'), list) else [metadata.get('authors', 'Unknown Author')]
            year = metadata.get('year', 'n.d.')
            journal = metadata.get('journal', 'Unknown Journal')
            volume = metadata.get('volume', '')
            issue = metadata.get('issue', '')
            pages = metadata.get('pages', '')
            doi = metadata.get('doi', doi)
            arxiv_id = metadata.get('arxiv_id', '')
            
            # 处理作者列表
            if isinstance(authors, list):
                if len(authors) > 3:
                    author_str = ', '.join(authors[:3]) + ' et al.'
                else:
                    author_str = ', '.join(authors)
            else:
                author_str = str(authors)
            
            # 生成不同格式的引用
            # BibTeX 格式
            bibtex_parts = [
                f"@article{{key{year},",
                f"  title={{{title}}},",
                f"  author={{{author_str}}},",
                f"  journal={{{journal}}},",
                f"  year={{{year}}}"
            ]
            if volume:
                bibtex_parts.append(f"  volume={{{volume}}}")
            if issue:
                bibtex_parts.append(f"  number={{{issue}}}")
            if pages:
                bibtex_parts.append(f"  pages={{{pages}}}")
            if arxiv_id:
                bibtex_parts.append(f"  eprint={{{arxiv_id}}}")
                bibtex_parts.append(f"  archivePrefix={{arXiv}}")
            if doi:
                bibtex_parts.append(f"  doi={{{doi}}}")
            
            bibtex_citation = ',\n'.join(bibtex_parts) + '\n}'
            
            # APA 格式
            vol_str = f', {volume}' if volume else ''
            issue_str = f'({issue})' if issue else ''
            pages_str = f', {pages}' if pages else ''
            
            if arxiv_id:
                apa_citation = f"{author_str} ({year}). {title}. *{journal}*{vol_str}{issue_str}{pages_str}. arXiv:{arxiv_id}"
            elif doi:
                apa_citation = f"{author_str} ({year}). {title}. *{journal}*{vol_str}{issue_str}{pages_str}. https://doi.org/{doi}"
            else:
                apa_citation = f"{author_str} ({year}). {title}. *{journal}*{vol_str}{issue_str}{pages_str}."
            
            # IEEE 格式
            vol_ieee = f', vol. {volume}' if volume else ''
            issue_ieee = f', no. {issue}' if issue else ''
            pages_ieee = f', pp. {pages}' if pages else ''
            
            if arxiv_id:
                ieee_citation = f'[1] {author_str}, "{title}," *{journal}*{vol_ieee}{issue_ieee}{pages_ieee}, {year}, arXiv:{arxiv_id}.'
            elif doi:
                ieee_citation = f'[1] {author_str}, "{title}," *{journal}*{vol_ieee}{issue_ieee}{pages_ieee}, {year}, doi: {doi}.'
            else:
                ieee_citation = f'[1] {author_str}, "{title}," *{journal}*{vol_ieee}{issue_ieee}{pages_ieee}, {year}.'
            
            vol_mla = f', vol. {volume}' if volume else ''
            issue_mla = f', no. {issue}' if issue else ''
            pages_mla = f', pp. {pages}' if pages else ''
            
            mla_citation = f'{author_str}. "{title}." *{journal}*{vol_mla}{issue_mla}, {year}{pages_mla}.'
            
            citations = {
                "bibtex": bibtex_citation,
                "apa": apa_citation,
                "ieee": ieee_citation,
                "mla": mla_citation
            }
            
            formatted_citation = citations.get(request.format, citations["bibtex"])
        else:
            # 如果无法验证，返回原始引用和警告
            formatted_citation = request.citation
            verified = False
        
        result = {
            "success": True,
            "original_citation": request.citation,
            "formatted_citation": formatted_citation,
            "format": request.format,
            "verified": verified,
            "metadata": metadata if verified else None,
            "warnings": [] if verified else ["无法自动验证引用，已返回原始格式。建议提供包含 DOI 的引用信息以获得更准确的结果。"]
        }
        
        logger.info(f"返回结果 - verified: {verified}, metadata: {metadata is not None}")
        if metadata:
            logger.info(f"Metadata keys: {list(metadata.keys())}")
        
        return result
        
    except Exception as e:
        logger.error(f"引用校验失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"校验失败: {str(e)}")

@router.post("/generate", response_model=Dict[str, Any])
async def generate_citation(request: CitationGenerateRequest):
    """生成引用格式"""
    try:
        # 模拟引用生成
        newline = "\n"
        quote = '"'
        citation_formats = {
            "bibtex": f"@article{{{request.authors or 'author2024'},{newline}  title={{{request.title or 'Title'}}},{newline}  author={{{request.authors or 'Author'}}},{newline}  journal={{{request.journal or 'Journal'}}},{newline}  year={{{request.year or 2024}}}{newline}}}",
            "apa": f"{request.authors or 'Author'} ({request.year or 2024}). {request.title or 'Title'}. *{request.journal or 'Journal'}*.",
            "ieee": f"[1] {request.authors or 'Author'}, {quote}{request.title or 'Title'},{quote} *{request.journal or 'Journal'}*, {request.year or 2024}.",
            "mla": f"{request.authors or 'Author'}. {quote}{request.title or 'Title'}.{quote} *{request.journal or 'Journal'}*, {request.year or 2024}."
        }
        
        citation = citation_formats.get(request.format, citation_formats["bibtex"])
        
        return {
            "success": True,
            "citation": citation,
            "format": request.format,
            "metadata": {
                "title": request.title,
                "authors": request.authors,
                "year": request.year,
                "journal": request.journal,
                "doi": request.doi
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"引用生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")

@router.get("/formats", response_model=Dict[str, Any])
async def get_citation_formats():
    """获取支持的引用格式"""
    try:
        formats = {
            "bibtex": {
                "name": "BibTeX",
                "description": "常用于LaTeX文档的引用格式",
                "example": "@article{key, title={Title}, author={Author}, year={2024}}"
            },
            "apa": {
                "name": "APA",
                "description": "美国心理学会格式，常用于社会科学",
                "example": "Author, A. (2024). Title. *Journal*, 1(1), 1-10."
            },
            "ieee": {
                "name": "IEEE",
                "description": "电气电子工程师学会格式，常用于工程技术",
                "example": "[1] A. Author, \"Title,\" *Journal*, vol. 1, no. 1, pp. 1-10, 2024."
            },
            "mla": {
                "name": "MLA",
                "description": "现代语言学会格式，常用于人文学科",
                "example": "Author. \"Title.\" *Journal*, vol. 1, no. 1, 2024, pp. 1-10."
            }
        }
        
        return {
            "success": True,
            "formats": formats,
            "total": len(formats)
        }
        
    except Exception as e:
        logger.error(f"获取引用格式失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")