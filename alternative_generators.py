"""
대안 AI 모델을 사용한 강의안 생성기
OpenAI가 불안정할 때 사용할 수 있는 백업 옵션들
"""
import os
import json
import requests
from typing import Dict, Any, Optional

class AlternativeLectureGenerator:
    """대안 AI 서비스를 사용한 강의안 생성"""
    
    def __init__(self):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        
    def generate_with_openai_simple(self, book_data: Dict[str, Any], lecture_preferences: Optional[Dict] = None) -> Dict:
        """OpenAI의 간단하고 빠른 프롬프트 사용"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            # 간단한 프롬프트로 빠른 생성
            prompt = self._create_simple_prompt(book_data, lecture_preferences)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 효율적인 강의안 작성 전문가입니다. 간결하지만 실용적인 강의안을 만드세요."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.5,
                max_tokens=2000,  # 토큰 수를 줄여서 빠른 생성
                timeout=30
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"OpenAI 간단 모드 실패: {str(e)}")
            return None
    
    def generate_with_anthropic(self, book_data: Dict[str, Any], lecture_preferences: Optional[Dict] = None) -> Dict:
        """Anthropic Claude를 사용한 강의안 생성"""
        if not self.anthropic_api_key:
            return None
            
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
            prompt = self._create_simple_prompt(book_data, lecture_preferences)
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.5,
                system="당신은 효율적인 강의안 작성 전문가입니다. JSON 형식으로 강의안을 작성하세요.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Claude 응답에서 JSON 추출
            content = response.content[0].text
            if '{' in content:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_content = content[json_start:json_end]
                return json.loads(json_content)
            
        except Exception as e:
            print(f"Anthropic 생성 실패: {str(e)}")
            return None
    
    def _create_simple_prompt(self, book_data: Dict[str, Any], lecture_preferences: Optional[Dict] = None) -> str:
        """간단하고 빠른 생성을 위한 프롬프트"""
        title = book_data.get('title', '')
        author = book_data.get('author', '')
        description = book_data.get('description', '')
        
        session_count = 3
        if lecture_preferences:
            session_count = int(lecture_preferences.get('session_count', 3))
        
        return f"""
다음 책 정보를 바탕으로 {session_count}강 강의안을 JSON으로 작성하세요.

책 제목: {title}
저자: {author}
소개: {description}

JSON 형식:
{{
  "lecture_overview": {{
    "title": "강의 제목",
    "description": "강의 설명",
    "target_audience": "대상",
    "duration": "총 시간"
  }},
  "lectures": [
    {{
      "lecture_number": 1,
      "title": "1강 제목",
      "duration": "90분",
      "objectives": ["목표1", "목표2"],
      "outline": [
        {{
          "section": "섹션명",
          "content": "구체적인 설명 (100-150자)",
          "time": "20분"
        }}
      ]
    }}
  ]
}}

간결하지만 실용적으로 작성하세요.
"""

def get_best_generator() -> Any:
    """가장 안정적인 생성기를 반환"""
    alt_gen = AlternativeLectureGenerator()
    
    # 1순위: OpenAI 간단 모드
    if alt_gen.openai_api_key:
        return ("openai_simple", alt_gen)
    
    # 2순위: Anthropic
    if alt_gen.anthropic_api_key:
        return ("anthropic", alt_gen)
    
    return (None, None)