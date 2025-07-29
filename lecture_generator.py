import os
import json
from openai import OpenAI

class LectureGenerator:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_lecture_plan(self, book_data, lecture_preferences=None):
        """
        책 정보와 사용자 선택사항을 바탕으로 강의안을 생성합니다.
        """
        try:
            # 책 정보 준비
            title = book_data.get('title', '')
            author = book_data.get('author', '')
            description = book_data.get('description', '')
            contents = book_data.get('contents', '')
            book_preview = book_data.get('book_preview', '')
            review_200 = book_data.get('review_200', '')
            
            # 프롬프트 생성 (사용자 선택사항 포함)
            prompt = self._create_lecture_prompt(title, author, description, contents, book_preview, review_200, lecture_preferences)
            
            # 시스템 메시지 생성 (스타일에 따라 조정)
            system_content = self._get_system_content(lecture_preferences)
            
            # API 키 확인
            if not self.api_key:
                print("OpenAI API 키가 설정되지 않았습니다.")
                return self._get_fallback_lecture_plan(title, lecture_preferences)
            
            print(f"OpenAI API 호출 중... (모델: gpt-4o)")
            
            # OpenAI API 호출 (타임아웃 추가)
            response = self.client.chat.completions.create(
                model="gpt-4o",  # 최신 모델 사용
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=4000,  # 더 상세한 내용을 위해 토큰 수 증가
                timeout=60  # 더 긴 응답을 위해 타임아웃 증가
            )
            
            # 응답 파싱
            lecture_plan = json.loads(response.choices[0].message.content)
            print("강의안 생성 완료!")
            
            # 사용자 선택사항을 강의안에 추가
            if lecture_preferences:
                lecture_plan['user_preferences'] = lecture_preferences
            
            return lecture_plan
            
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {str(e)}")
            return self._get_fallback_lecture_plan(title, lecture_preferences)
        except Exception as e:
            error_msg = str(e)
            print(f"강의안 생성 중 오류 발생: {error_msg}")
            
            # 다양한 오류 유형에 따른 구체적인 메시지
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                print("⚠️ OpenAI API 응답 시간 초과. 네트워크 연결을 확인해주세요.")
            elif "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                print("⚠️ OpenAI API 키가 유효하지 않습니다. API 키를 확인해주세요.")
            elif "rate_limit" in error_msg.lower():
                print("⚠️ API 호출 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                print("⚠️ 네트워크 연결 문제가 발생했습니다. 인터넷 연결을 확인해주세요.")
            else:
                print(f"⚠️ 예상치 못한 오류: {error_msg}")
            
            return {
                'error': True,
                'error_message': f'강의안 생성 실패: {error_msg}',
                'fallback_plan': self._get_fallback_lecture_plan(title, lecture_preferences)
            }
    
    def _create_lecture_prompt(self, title, author, description, contents, book_preview, review_200, lecture_preferences=None):
        """강의안 생성을 위한 프롬프트를 만듭니다."""
        
        # 사용자 선택사항에 따른 요구사항 조정
        session_count = "3-4강"
        session_duration = "60-90분"
        style_description = ""
        level_description = ""
        
        if lecture_preferences:
            session_count = f"{lecture_preferences.get('session_count', '4')}강"
            session_duration = f"{lecture_preferences.get('session_duration', '90')}분"
            
            # 스타일에 따른 설명
            style_map = {
                'theoretical': '이론 중심으로 개념과 원리를 깊이 있게 다루며',
                'practical': '실습과 실무 사례를 중심으로 하여',
                'discussion': '상호작용과 토론을 활발히 활용하며',
                'case_study': '실제 사례 분석을 통해 학습하며',
                'workshop': '참여형 활동과 그룹 작업을 중심으로',
                'seminar': '발표와 질의응답을 중심으로'
            }
            style_description = style_map.get(lecture_preferences.get('lecture_style', ''), '')
            
            # 수준에 따른 설명
            level_map = {
                'beginner': '초보자도 이해할 수 있도록 기초부터 설명하며',
                'intermediate': '기본 지식을 보유한 학습자를 대상으로',
                'advanced': '전문가 수준의 깊이 있는 내용으로',
                'mixed': '다양한 수준의 학습자를 고려하여'
            }
            level_description = level_map.get(lecture_preferences.get('target_level', ''), '')
        
        prompt = f"""
다음 책 정보를 바탕으로 {session_count} 분량의 체계적인 강의안을 JSON 형식으로 작성해주세요.

**책 정보:**
- 제목: {title}
- 저자: {author}
- 책 소개: {description}
- 차례: {contents}
- 책속으로: {book_preview}
- 200자평: {review_200}

**요구사항:**
1. {session_count}으로 구성된 강의 계획
2. 각 강의는 {session_duration} 분량
3. {style_description} 강의 스타일로 구성
4. {level_description} 적절한 난이도 설정
5. 단계별 학습 목표 제시
6. 각 강의의 outline은 최소 5-7개의 세부 섹션으로 구성
7. 각 섹션마다 구체적인 내용, 활동, 시간 배분을 상세히 포함
8. **중요**: 각 섹션에는 실제 강의에서 사용할 수 있는 상세한 텍스트 내용을 포함
9. 섹션별로 3개의 상세 설명을 각각 200-300자 분량으로 작성 (총 600-900자)
10. 실무 예제, 실습 과제, 토론 주제를 풍부하게 제시
11. 각 강의마다 핵심 개념 5-7개, 활동 3-5개를 포함
12. 슬라이드나 교재에 들어갈 수 있는 수준의 상세한 내용 제공
{f'13. 특별 강조사항: {lecture_preferences.get("special_focus", "")}' if lecture_preferences and lecture_preferences.get("special_focus") else ""}

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
          "content": "강의에서 실제로 설명할 상세한 내용 (최소 200-300자). 개념 정의, 예시, 설명 등을 포함하여 강사가 그대로 활용할 수 있는 수준으로 작성",
          "detailed_explanations": [
            {{
              "title": "핵심 개념 설명",
              "content": "해당 섹션의 가장 중요한 개념을 자세히 설명. 정의, 특징, 원리 등을 포함하여 200-300자로 작성"
            }},
            {{
              "title": "실무적 관점",
              "content": "실제 현장에서 어떻게 적용되는지, 왜 중요한지를 구체적으로 설명. 200-300자로 작성"
            }},
            {{
              "title": "학습 포인트",
              "content": "학습자가 반드시 알아야 할 핵심 내용과 주의사항을 정리. 200-300자로 작성"
            }}
          ],
          "examples": ["구체적인 예시1", "구체적인 예시2", "실제 사례"],
          "activities": "실습 또는 토론 활동",
          "materials": "필요한 자료나 도구",
          "key_points": ["핵심 포인트1", "핵심 포인트2", "핵심 포인트3"],
          "time": "시간 배분"
        }},
        {{
          "section": "다음 섹션명",
          "content": "마찬가지로 상세한 강의 내용 (최소 200-300자)",
          "detailed_explanations": [
            {{
              "title": "핵심 개념 설명",
              "content": "해당 섹션의 핵심 내용 상세 설명"
            }},
            {{
              "title": "실무적 관점", 
              "content": "실제 적용 사례와 중요성"
            }},
            {{
              "title": "학습 포인트",
              "content": "꼭 기억해야 할 핵심 사항들"
            }}
          ],
          "examples": ["예시들"],
          "activities": "관련 활동",
          "materials": "필요 자료",
          "key_points": ["중요 포인트들"],
          "time": "시간"
        }}
      ],
      "key_concepts": ["핵심개념1", "핵심개념2", "핵심개념3", "핵심개념4", "핵심개념5"],
      "activities": ["실습활동1", "토론주제1", "과제1", "발표1", "팀프로젝트1"],
      "homework": ["과제 내용"],
      "reading_materials": ["추천 읽기 자료"],
      "practical_examples": ["실무 예제1", "실무 예제2"]
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

**중요 지침:**
1. 각 섹션의 "content"와 "detailed_explanations"에는 강사가 실제로 말할 수 있는 구체적인 내용을 작성하세요
2. detailed_explanations는 반드시 3개 항목으로 구성하고, 각각 200-300자로 작성하세요
3. 첫 번째는 "핵심 개념 설명", 두 번째는 "실무적 관점", 세 번째는 "학습 포인트"로 구성하세요
4. 단순한 키워드나 제목이 아닌, 완전한 설명 문장으로 작성하세요
5. 예를 들어 "AI의 기본 개념"이라면, AI가 무엇인지, 특징, 작동 원리를 각각 다른 관점에서 3번 설명하세요
6. 각 섹션은 할당된 시간에 맞는 충분한 내용량을 포함해야 합니다
7. 실제 강의실에서 바로 사용할 수 있는 수준의 상세함을 제공하세요

책의 내용과 수준을 고려하여 풍부하고 상세한 강의안을 구성해주세요.
"""
        return prompt
    
    def _get_system_content(self, lecture_preferences):
        """사용자 선택사항에 따른 시스템 메시지를 생성합니다."""
        base_content = """당신은 전문적인 강의 설계 전문가입니다. 주어진 책 정보를 바탕으로 체계적이고 실용적인 강의안을 만드는 것이 목표입니다. 

중요: 각 섹션의 내용은 강사가 실제 강의에서 그대로 활용할 수 있을 정도로 상세하고 구체적으로 작성해야 합니다. 단순한 제목이나 키워드가 아닌, 실제 설명할 내용을 문장으로 풀어서 작성하세요."""
        
        if not lecture_preferences:
            return base_content
        
        style_instructions = {
            'theoretical': " 이론적 배경과 개념 설명을 중시하며, 학문적 깊이를 추구하는 강의를 설계하세요.",
            'practical': " 실무 적용과 실습 활동을 중심으로 하는 실용적인 강의를 설계하세요.",
            'discussion': " 학습자 간 상호작용과 토론을 활발히 유도하는 참여형 강의를 설계하세요.",
            'case_study': " 실제 사례 분석과 문제 해결 중심의 강의를 설계하세요.",
            'workshop': " 그룹 활동과 협업 프로젝트를 중심으로 하는 워크숍형 강의를 설계하세요.",
            'seminar': " 발표와 질의응답, 학술적 토론을 중심으로 하는 세미나형 강의를 설계하세요."
        }
        
        level_instructions = {
            'beginner': " 초보자도 쉽게 따라할 수 있도록 단계별로 친절하게 설명하세요.",
            'intermediate': " 기본 지식을 가진 학습자에게 적절한 도전과 발전을 제공하세요.",
            'advanced': " 전문가 수준의 심화된 내용과 고급 기법을 다루세요.",
            'mixed': " 다양한 수준의 학습자를 모두 고려한 차별화된 학습 경험을 제공하세요."
        }
        
        style = lecture_preferences.get('lecture_style', '')
        level = lecture_preferences.get('target_level', '')
        
        additional_content = ""
        if style in style_instructions:
            additional_content += style_instructions[style]
        if level in level_instructions:
            additional_content += level_instructions[level]
        
        return base_content + additional_content
    
    def _get_fallback_lecture_plan(self, title, lecture_preferences=None):
        """API 호출 실패시 사용할 기본 강의안"""
        
        # 사용자 선택사항 적용
        session_count = 3
        session_duration = "2시간"
        total_duration = "총 6시간"
        
        if lecture_preferences:
            session_count = int(lecture_preferences.get('session_count', 3))
            duration_minutes = int(lecture_preferences.get('session_duration', 120))
            session_duration = f"{duration_minutes}분"
            total_duration = f"총 {duration_minutes * session_count // 60}시간"
        
        # 기본 강의 구성
        lectures = []
        for i in range(session_count):
            lecture = {
                "lecture_number": i + 1,
                "title": f"{i + 1}강: 기본 주제 {i + 1}",
                "duration": session_duration,
                "objectives": ["기본 개념 이해", "실무 적용"],
                "outline": [
                    {
                        "section": "도입",
                        "content": "주제 소개 및 학습 목표",
                        "time": "20분"
                    },
                    {
                        "section": "핵심 내용",
                        "content": "주요 내용 설명",
                        "time": f"{duration_minutes - 40}분"
                    },
                    {
                        "section": "정리",
                        "content": "요약 및 다음 강의 예고",
                        "time": "20분"
                    }
                ],
                "key_concepts": ["핵심개념1", "핵심개념2"],
                "activities": ["학습 활동", "질의응답"]
            }
            lectures.append(lecture)
        
        fallback_plan = {
            "lecture_overview": {
                "title": f"{title} 심화 과정",
                "description": "책 내용을 바탕으로 한 체계적인 학습 과정입니다.",
                "target_audience": "관련 분야 학습자",
                "duration": f"{total_duration} ({session_count}강)",
                "learning_objectives": [
                    "책의 핵심 개념 이해",
                    "실무 적용 방법 습득",
                    "심화 학습 방향 설정"
                ]
            },
            "lectures": lectures,
            "assessment": {
                "methods": ["과제 평가", "참여도 평가"],
                "criteria": "이해도와 참여도를 종합 평가"
            },
            "resources": {
                "required": [title],
                "recommended": ["관련 참고 자료"]
            }
        }
        
        # 사용자 선택사항 추가
        if lecture_preferences:
            fallback_plan['user_preferences'] = lecture_preferences
        
        return fallback_plan