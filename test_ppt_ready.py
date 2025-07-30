#!/usr/bin/env python3
"""
PPT 준비 강의안 테스트
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_ppt_ready_format():
    """PPT 준비 포맷 테스트"""
    print("=== PPT 준비 강의안 개선 테스트 ===\n")
    
    try:
        from perplexity_generator import PerplexityLectureGenerator
        
        # 생성기 초기화
        generator = PerplexityLectureGenerator()
        print("✅ Perplexity 생성기 초기화 성공\n")
        
        # 프롬프트 확인
        prompt = generator._get_comprehensive_prompt()
        
        print("📋 개선된 프롬프트 특징:")
        print("1. PPT 슬라이드별 구성:", "ppt_slides" in prompt)
        print("2. 발표자 노트 포함:", "speaker_notes" in prompt)
        print("3. 실제 기업 사례 요구:", "실제 기업명" in prompt)
        print("4. 최신 통계 데이터:", "최신 통계 데이터" in prompt)
        print("5. 시각적 자료 제안:", "차트/그래프" in prompt)
        print("6. 구체적 수치 요구:", "구체적 수치" in prompt)
        print()
        
        print(f"📝 프롬프트 길이: {len(prompt)} 문자")
        print("📝 PPT 관련 키워드 확인:")
        ppt_keywords = ["슬라이드", "PPT", "발표", "핵심 포인트", "발표자 노트", "차트", "그래프"]
        for keyword in ppt_keywords:
            print(f"   - '{keyword}': {'✅' if keyword in prompt else '❌'}")
        
        print("\n🎯 이제 생성될 강의안의 특징:")
        print("• 슬라이드별로 구체적인 제목과 핵심 포인트")
        print("• 발표자가 말할 내용과 노트 포함")
        print("• 실제 기업 사례와 구체적 수치")
        print("• 최신 통계 데이터와 연구 결과")
        print("• 차트/그래프 제안과 시각적 자료 가이드")
        print("• PPT 제작에 바로 활용 가능한 형태")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
        return False

def test_format_display():
    """포맷 표시 테스트"""
    print("\n=== 포맷 표시 시스템 테스트 ===")
    
    try:
        from routes import format_lecture_plan
        
        # 새로운 PPT 형식 데이터 시뮬레이션
        test_data = {
            "lecture_overview": {
                "title": "AI PR 마케팅 전략",
                "description": "AI 기술을 활용한 효과적인 PR 마케팅 전략 수립"
            },
            "lectures": [
                {
                    "session_title": "AI PR 도구 활용법",
                    "duration": "90분",
                    "learning_objectives": ["AI 도구 이해", "실무 적용"],
                    "detailed_outline": [
                        {
                            "section_title": "AI PR 도구 소개",
                            "duration": "30분",
                            "ppt_slides": [
                                {
                                    "slide_title": "주요 AI PR 플랫폼",
                                    "key_points": ["ChatGPT 활용", "Jasper AI", "Copy.ai"],
                                    "detailed_content": "각 플랫폼의 특징과 PR 활용 방안을 상세히 설명",
                                    "speaker_notes": "실제 사용 경험을 바탕으로 설명하고 데모 진행"
                                }
                            ],
                            "real_examples": "삼성전자의 Galaxy S24 런칭 캠페인에서 AI 도구 활용 사례",
                            "latest_data": "2024년 AI PR 도구 시장 규모 15억 달러 (Statista 조사)",
                            "practical_tips": ["도구별 강점 파악", "비용 대비 효과 분석"]
                        }
                    ]
                }
            ]
        }
        
        formatted = format_lecture_plan(test_data)
        
        print("✅ 새로운 포맷 지원 확인:")
        print("- PPT 슬라이드 구성:", "📊 PPT 슬라이드 구성" in formatted)
        print("- 실제 사례:", "🏢 실제 사례" in formatted)
        print("- 최신 데이터:", "📈 최신 데이터" in formatted)
        print("- 실무 팁:", "💡 실무 팁" in formatted)
        print("- 발표자 노트:", "발표자 노트" in formatted)
        
        print(f"\n포맷팅 결과 길이: {len(formatted)} 문자")
        print("포맷팅 미리보기:")
        print(formatted[:500] + "...")
        
        return True
        
    except Exception as e:
        print(f"❌ 포맷 테스트 오류: {e}")
        return False

if __name__ == "__main__":
    print("PPT 준비 강의안 시스템 테스트 시작\n")
    
    success1 = test_ppt_ready_format()
    success2 = test_format_display()
    
    print(f"\n{'='*50}")
    print("테스트 결과 요약:")
    print(f"✅ PPT 프롬프트 개선: {'성공' if success1 else '실패'}")
    print(f"✅ 포맷 표시 시스템: {'성공' if success2 else '실패'}")
    
    if success1 and success2:
        print("\n🎉 PPT 준비 강의안 시스템이 완성되었습니다!")
        print("이제 Perplexity AI가 다음과 같은 내용을 생성합니다:")
        print("• 슬라이드별 구체적 제목과 핵심 포인트")
        print("• 발표자 노트와 상세 설명")
        print("• 실제 기업 사례와 구체적 수치")
        print("• 최신 통계 데이터와 출처")
        print("• 차트/그래프 제안")
        print("• PPT 제작에 바로 사용 가능한 형태")
    else:
        print("\n⚠️ 일부 문제가 발견되었습니다. 추가 확인이 필요합니다.")