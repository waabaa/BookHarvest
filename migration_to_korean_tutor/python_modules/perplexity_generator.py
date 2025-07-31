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
                        "content": "당신은 세계 최고 수준의 경영 컨설턴트이자 PPT 제작 전문가입니다. 맥킨지, BCG, 베인 수준의 깊이 있는 분석과 하버드 비즈니스 스쿨 수준의 사례 연구를 바탕으로 PPT 발표에 바로 사용할 수 있는 완벽한 강의안을 작성합니다. 반드시 온라인 검색을 통해 2023-2024년 최신 데이터를 확인하고, Fortune 500 기업들의 실제 사례, 구체적 투자 규모, ROI 수치, 성과 지표를 포함하여 발표자가 그대로 읽을 수 있는 완전한 문장으로 작성합니다. 4차 산업혁명 시대의 배경부터 시작하여 체계적이고 논리적인 구조로 내용을 전개합니다."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 8000,
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
        """종합형 강의 교안 프롬프트 - 매우 상세하고 풍부한 내용"""
        return """다음 도서를 바탕으로 대학원 수준의 매우 상세하고 실무적인 강의안을 작성해주세요.

반드시 다음 JSON 형식으로 응답해주세요:

{
  "lecture_overview": {
    "title": "강의 제목",
    "description": "강의 개요 (최소 300자, 구체적이고 상세하게)",
    "target_audience": "대상 학습자",
    "duration": "총 강의 시간",
    "learning_outcomes": ["핵심 학습성과1", "핵심 학습성과2", "핵심 학습성과3"],
    "prerequisites": "선수 지식/조건"
  },
  "lectures": [
    {
      "session_title": "세션 제목",
      "duration": "90분",
      "learning_objectives": ["구체적 학습목표1", "구체적 학습목표2", "구체적 학습목표3"],
      "detailed_outline": [
        {
          "section_title": "섹션 제목",
          "duration": "30분",
          "ppt_slides": [
            {
              "slide_number": 1,
              "slide_title": "슬라이드 제목",
              "key_points": ["핵심 포인트 1", "핵심 포인트 2", "핵심 포인트 3"],
              "detailed_content": "PPT 발표용 상세 설명 (최소 500자). 4차 산업혁명 시대 배경부터 시작하여 해당 주제의 중요성, 핵심 원칙, 구체적 방법론, 실행 단계까지 체계적으로 설명. 실제 기업명과 구체적 사례, 수치 데이터를 반드시 포함하여 발표자가 그대로 읽을 수 있도록 완전한 문장으로 작성",
              "visual_suggestions": "차트/그래프/이미지 제안",
              "speaker_notes": "발표자 노트 (최소 200자). 슬라이드 내용을 보완하는 추가 설명, 청중과의 상호작용 방법, 강조해야 할 포인트, 예상 질문과 답변 등 실제 발표 상황에서 활용할 수 있는 구체적 가이드"
            }
          ],
          "real_examples": "실제 기업 성공/실패 사례 (최소 300자). 아마존, UPS, 코카콜라, 넷플릭스, 세포라 등 글로벌 기업들의 구체적 프로젝트명, 투자 규모, 성과 수치, 절감 효과 등을 상세히 기술. 실패 사례도 포함하여 반면교사로 활용",
          "latest_data": "2023-2024년 최신 통계/연구 데이터 (출처 필수). 시장 규모, 성장률, 투자 동향, ROI 데이터 등 구체적 수치와 함께 출처(맥킨지, BCG, 딜로이트 등) 명시",
          "practical_tips": ["CEO가 바로 적용할 수 있는 구체적 실무 팁 1 (체크리스트 형태)", "경영진 회의에서 활용할 수 있는 실무 팁 2", "조직 내 실행을 위한 구체적 단계별 가이드 3", "성과 측정과 ROI 산출을 위한 실무 팁 4"]
        }
      ],
      "key_concepts": ["핵심개념1", "핵심개념2", "핵심개념3", "핵심개념4"],
      "practical_applications": "실무 적용 방안과 구체적 방법론 (최소 200자)",
      "case_studies": "실제 기업/조직 사례 분석 (최소 150자)",
      "discussion_topics": ["토론주제1", "토론주제2", "토론주제3"],
      "assessment_methods": "평가 기준과 방법 상세 설명",
      "recommended_readings": ["추천자료1", "추천자료2", "추천자료3"]
    }
  ],
  "additional_resources": {
    "industry_trends": "업계 최신 동향과 미래 전망 (최소 200자)",
    "expert_insights": "전문가 의견과 인사이트",
    "practical_tools": ["실무 도구1", "실무 도구2", "실무 도구3"],
    "certification_info": "관련 자격증이나 인증 정보"
  }
}

작성 요구사항:
- 4-5개의 강의 세션으로 구성 (각 90분)
- 각 세션을 PPT 발표에 바로 사용할 수 있도록 슬라이드별로 구성
- 슬라이드마다 핵심 포인트, 상세 내용, 발표자 노트 포함
- 실제 기업명, 구체적 수치, 최신 통계 데이터를 반드시 포함 (연도와 출처 명시)
- 시각적 자료 제안 (차트, 그래프, 이미지 등)
- 실무에서 바로 활용할 수 있는 구체적 도구와 방법론
- 최신 업계 트렌드와 연구 결과 인용

PPT 제작을 위한 필수 요소:
1. 슬라이드별 명확한 제목과 핵심 메시지
2. 발표자가 말할 구체적 내용과 발표 노트
3. 실제 기업 사례 (회사명, 캠페인명, 성과 수치 포함)
4. 최신 통계 데이터와 연구 결과 (2023-2024년 데이터 우선)
5. 차트나 그래프로 표현할 수 있는 데이터 제안
6. 청중 참여를 위한 질문이나 토론 포인트
7. 실무 적용을 위한 체크리스트나 가이드라인

검색 활용 지침 (반드시 온라인 검색 실행):
- 2023-2024년 최신 업계 보고서 검색: 맥킨지, BCG, 딜로이트, PwC 등 컨설팅 보고서
- Fortune 500 기업들의 AI 전략 사례: 투자 규모, ROI, 성과 지표 포함
- 글로벌 기업 성공/실패 사례: 아마존, 구글, 마이크로소프트, 삼성, LG 등
- 최신 기술 동향: Gartner, IDC 시장 분석 보고서
- 업계 통계: 시장 규모, 성장률, 채택률 등 구체적 수치
- CEO/경영진 인터뷰: 하버드 비즈니스 리뷰, MIT 슬론 등 권위 있는 매체

중요: 모든 내용은 검색을 통해 확인된 최신 정보여야 하며, 가상의 데이터나 추정치 사용 금지"""
    
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