import os
import json
from openai import OpenAI

class LectureGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def generate_lecture_plan(self, book_data):
        """
        책 정보를 바탕으로 3-4강 분량의 강의안을 생성합니다.
        """
        try:
            # 책 정보 준비
            title = book_data.get('title', '')
            author = book_data.get('author', '')
            description = book_data.get('description', '')
            contents = book_data.get('contents', '')
            book_preview = book_data.get('book_preview', '')
            review_200 = book_data.get('review_200', '')
            
            # 프롬프트 생성
            prompt = self._create_lecture_prompt(title, author, description, contents, book_preview, review_200)
            
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model="gpt-4o",  # 최신 모델 사용
                messages=[
                    {"role": "system", "content": "당신은 전문적인 강의 설계 전문가입니다. 주어진 책 정보를 바탕으로 체계적이고 실용적인 강의안을 만드는 것이 목표입니다."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2000
            )
            
            # 응답 파싱
            lecture_plan = json.loads(response.choices[0].message.content)
            return lecture_plan
            
        except Exception as e:
            print(f"강의안 생성 중 오류 발생: {str(e)}")
            return self._get_fallback_lecture_plan(book_data.get('title', ''))
    
    def _create_lecture_prompt(self, title, author, description, contents, book_preview, review_200):
        """강의안 생성을 위한 프롬프트를 만듭니다."""
        
        prompt = f"""
다음 책 정보를 바탕으로 3-4강 분량의 체계적인 강의안을 JSON 형식으로 작성해주세요.

**책 정보:**
- 제목: {title}
- 저자: {author}
- 책 소개: {description}
- 차례: {contents}
- 책속으로: {book_preview}
- 200자평: {review_200}

**요구사항:**
1. 3-4강으로 구성된 강의 계획
2. 각 강의는 60-90분 분량
3. 실무에 적용 가능한 내용 포함
4. 이론과 실습의 균형 유지
5. 단계별 학습 목표 제시

**JSON 형식:**
{{
  "lecture_overview": {{
    "title": "강의 전체 제목",
    "description": "강의 전체 소개 (2-3줄)",
    "target_audience": "대상 수강생",
    "duration": "총 강의 시간",
    "learning_objectives": ["학습목표1", "학습목표2", "학습목표3"]
  }},
  "lectures": [
    {{
      "lecture_number": 1,
      "title": "1강 제목",
      "duration": "90분",
      "objectives": ["1강 목표1", "1강 목표2"],
      "outline": [
        {{
          "section": "섹션명",
          "content": "구체적 내용",
          "time": "30분"
        }}
      ],
      "key_concepts": ["핵심개념1", "핵심개념2"],
      "activities": ["실습활동1", "토론주제1"]
    }}
  ],
  "assessment": {{
    "methods": ["평가방법1", "평가방법2"],
    "criteria": "평가기준 설명"
  }},
  "resources": {{
    "required": ["필수자료1", "필수자료2"],
    "recommended": ["추천자료1", "추천자료2"]
  }}
}}

책의 내용과 수준을 고려하여 적절한 난이도로 강의안을 구성해주세요.
"""
        return prompt
    
    def _get_fallback_lecture_plan(self, title):
        """API 호출 실패시 사용할 기본 강의안"""
        return {
            "lecture_overview": {
                "title": f"{title} 심화 과정",
                "description": "책 내용을 바탕으로 한 체계적인 학습 과정입니다.",
                "target_audience": "관련 분야 학습자",
                "duration": "총 6시간 (3강)",
                "learning_objectives": [
                    "책의 핵심 개념 이해",
                    "실무 적용 방법 습득",
                    "심화 학습 방향 설정"
                ]
            },
            "lectures": [
                {
                    "lecture_number": 1,
                    "title": "기초 개념과 이론",
                    "duration": "2시간",
                    "objectives": ["기본 개념 이해", "이론적 배경 학습"],
                    "outline": [
                        {
                            "section": "도입",
                            "content": "주제 소개 및 학습 목표",
                            "time": "20분"
                        },
                        {
                            "section": "핵심 이론",
                            "content": "책의 주요 이론 설명",
                            "time": "80분"
                        },
                        {
                            "section": "정리",
                            "content": "요약 및 다음 강의 예고",
                            "time": "20분"
                        }
                    ],
                    "key_concepts": ["핵심개념1", "핵심개념2"],
                    "activities": ["개념 정리", "질의응답"]
                }
            ],
            "assessment": {
                "methods": ["과제 평가", "참여도 평가"],
                "criteria": "이해도와 참여도를 종합 평가"
            },
            "resources": {
                "required": [title],
                "recommended": ["관련 참고 자료"]
            }
        }