import os
import json
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PerplexityLectureGenerator:
    """Perplexity AI를 활용한 고급 강의안 생성기"""
    
    def __init__(self):
        self.api_key = os.environ.get('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable is required")
        
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 5가지 프롬프트 템플릿 정의
        self.prompt_templates = {
            "comprehensive": self._get_comprehensive_prompt(),
            "slide_summary": self._get_slide_summary_prompt(), 
            "deep_analysis": self._get_deep_analysis_prompt(),
            "practical_focus": self._get_practical_focus_prompt(),
            "citation_enhanced": self._get_citation_enhanced_prompt()
        }
    
    def generate_lecture_plan(self, book_data: Dict[str, Any], preferences: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """메인 강의안 생성 메서드"""
        try:
            # 사용자 선택에 따른 프롬프트 스타일 결정
            lecture_style = preferences.get('lecture_style', 'comprehensive')
            
            # 기본 정보 추출
            title = book_data.get('title', '')
            contents = book_data.get('contents', '')
            description = book_data.get('description', '')
            pdf_content = book_data.get('pdf_content', '')
            
            # 책 내용 종합
            book_content = self._prepare_book_content(book_data)
            
            # 프롬프트 생성
            prompt = self._create_enhanced_prompt(book_content, preferences, lecture_style)
            
            # Perplexity API 호출
            response = self._call_perplexity_api(prompt)
            
            if response and response.get('choices'):
                content = response['choices'][0]['message']['content']
                citations = response.get('citations', [])
                
                return {
                    'title': f"{title} - 강의안",
                    'content': content,
                    'citations': citations,
                    'style': lecture_style,
                    'preferences': preferences,
                    'generated_by': 'perplexity'
                }
            else:
                logger.error("Perplexity API returned empty response")
                return None
                
        except Exception as e:
            logger.error(f"Error generating lecture plan with Perplexity: {str(e)}")
            return None
    
    def _prepare_book_content(self, book_data: Dict[str, Any]) -> str:
        """책 내용을 강의안 생성용으로 정리"""
        content_parts = []
        
        if book_data.get('title'):
            content_parts.append(f"도서명: {book_data['title']}")
        
        if book_data.get('author'):
            content_parts.append(f"저자: {book_data['author']}")
            
        if book_data.get('description'):
            content_parts.append(f"도서 소개:\n{book_data['description']}")
            
        if book_data.get('contents'):
            content_parts.append(f"목차:\n{book_data['contents']}")
            
        if book_data.get('book_preview'):
            content_parts.append(f"책 미리보기:\n{book_data['book_preview']}")
            
        if book_data.get('review_200'):
            content_parts.append(f"200자평:\n{book_data['review_200']}")
            
        if book_data.get('pdf_content'):
            content_parts.append(f"첨부 PDF 내용:\n{book_data['pdf_content'][:2000]}...")
            
        return "\n\n".join(content_parts)
    
    def _create_enhanced_prompt(self, book_content: str, preferences: Dict[str, Any], style: str) -> str:
        """향상된 프롬프트 생성"""
        base_template = self.prompt_templates.get(style, self.prompt_templates['comprehensive'])
        
        # 사용자 맞춤 설정 적용
        target_level = preferences.get('target_level', '중급')
        session_count = preferences.get('session_count', '3')
        session_duration = preferences.get('session_duration', '90분')
        special_focus = preferences.get('special_focus', '')
        
        customization = f"""
강의 대상 수준: {target_level}
강의 세션 수: {session_count}회
세션당 시간: {session_duration}
특별 강조사항: {special_focus if special_focus else '없음'}
"""
        
        return f"""
{base_template}

=== 강의 설정 ===
{customization}

=== 도서 정보 ===
{book_content}

위 정보를 바탕으로 {session_count}회차 강의용 교안을 상세히 작성해주세요.
각 회차마다 학습목표, 핵심개념, 실습/사례, Q&A, 평가문제를 포함하고,
최신 연구동향과 실무 사례를 반드시 인용하여 포함해주세요.
"""
    
    def _call_perplexity_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Perplexity API 호출"""
        try:
            payload = {
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "당신은 대학교 강의 교안 작성 전문가입니다. 최신 연구 동향과 실무 사례를 인용하여 실질적이고 체계적인 강의안을 작성합니다."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.3,
                "top_p": 0.9,
                "return_citations": True,
                "search_recency_filter": "month",
                "stream": False
            }
            
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error("Perplexity API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Perplexity API request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling Perplexity API: {str(e)}")
            return None
    
    def _get_comprehensive_prompt(self) -> str:
        """종합형 강의 교안 프롬프트"""
        return """
각 장별로 강의 교안을 작성해주세요.

각 장마다 다음 항목을 모두 포함해 주세요:

**학습 목표** (3~5가지 구체적으로)

**핵심 개념 정리** (서술형 요약 및 주요 키워드, 개념 정의)

**시각 자료** (목록이나 표, 다이어그램 형식 서술)

**실전 사례 또는 역사적 사례** (업계/학계 최신 동향 포함, 필요시 연도/출처도 명시)

**Q&A** (학생이 자주 묻는 3개 질문+답변)

**예상 평가 문제** (객관식 2개, 서술형 2개, 정답 포함)

**추가 읽을거리** (최신 논문, 기사 제목+간단 설명, 2개 이상)

가능한 한 마크다운 표와 리스트, 문단을 적절히 혼합해서 가독성 높게 작성하세요.
"""
    
    def _get_slide_summary_prompt(self) -> str:
        """슬라이드용 요약 프롬프트"""
        return """
대학 강의용 슬라이드 문서를 작성해주세요.
각 장별로 다음 요소 포함:

**제목 슬라이드** (장 제목, 소주제 목록)

**핵심 메시지** 한 문장

**주요 개념/핵심 이론** (슬라이드 적합하게 간결 요약)

**간단 도식, 표, 핵심 용어 정리**

**시각적 인상 강화할 예시** (간단 그래프/이미지 설명 문구)

**학습TIP, 관련 실무 팁** (1~2개)

**마지막에 요점 정리/슬라이드 퀴즈** (2문항)
"""
    
    def _get_deep_analysis_prompt(self) -> str:
        """심화 챕터별 인사이트 프롬프트"""
        return """
각 장별로 다음과 같이 심화 분석 강의안을 작성해주세요.

**핵심 질문** (학생 이해를 위한 열린 질문 2개)

**이론적 쟁점과 다양한 견해** (학자별 주장 명확히 비교)

**최근 연구 동향** (최근 2년간 발표 논문/보고서 요약)

**실제 현장 사례** (산업계, 사회 현상 등 구체적 데이터/사례 중심)

**논쟁거리 및 비판적 시각** (다양한 시각, 반론 요약)

**향후 연구 혹은 실무 적용 아이디어** (창의적 제안 2가지)
"""
    
    def _get_practical_focus_prompt(self) -> str:
        """실전 문제 중심 교안 프롬프트"""
        return """
각 장별로 다음을 포함한 실전 중심 교안 제작:

**실제 현장 적용 시나리오** (한 사례씩, 단계별 설명)

**문제 인식→해결 방법 도출 과정** (마크다운 표로 단계별 제시)

**학생 참여 토론 질문** 2개 (실제 적용 고민하게 하는 문제)

**비슷한 사례 비교 분석** (의미 있는 유사 사례 포함)

**수행평가 예시** (현장/프로젝트형 평가 루브릭 간단 제시)
"""
    
    def _get_citation_enhanced_prompt(self) -> str:
        """AI 검색 및 최신 정보 인용형 프롬프트"""
        return """
각 장의 개념, 이론을 설명할 때 반드시 최근 2년 이내 논문, 뉴스, 업계 동향 등을 자동 인용해서 '인용/참고' 박스에 넣어주세요.

각 인용자료는 출처와 1~2줄 요약 추가.

해당 인용 내용이 본문 어디에 반영되어야 할지 명확히 표시해주세요.

**최신 동향 및 인용 자료**를 풍부하게 포함하여 작성해주세요.
"""

# 전역 인스턴스 생성
_perplexity_instance = None

def get_perplexity_generator():
    """Perplexity 생성기 싱글톤 인스턴스 반환"""
    global _perplexity_instance
    if _perplexity_instance is None:
        try:
            _perplexity_instance = PerplexityLectureGenerator()
        except Exception as e:
            logger.error(f"Failed to initialize Perplexity generator: {str(e)}")
            _perplexity_instance = None
    return _perplexity_instance