#!/usr/bin/env python3
"""
강의안 생성 기능 단위 테스트
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

def test_format_lecture_plan():
    """format_lecture_plan 함수 테스트"""
    from routes import format_lecture_plan
    
    print("=== format_lecture_plan 함수 테스트 ===")
    
    # 테스트 데이터 1: 기본 강의안
    test_data_1 = {
        "title": "테스트 강의안",
        "content": "## 1강: 소개\n\n이것은 테스트입니다.\n\n**중요**: 핵심 내용\n\n- 항목 1\n- 항목 2",
        "generated_at": "2025-07-29 23:45:00"
    }
    
    result_1 = format_lecture_plan(test_data_1)
    print("테스트 1 결과:")
    print(result_1)
    print()
    
    # 테스트 데이터 2: Perplexity AI 결과 (인용 포함)
    test_data_2 = {
        "title": "AI 강의안 - Perplexity 생성",
        "content": "### 1. 개요\n\nAI 기술의 발전\n\n### 2. 핵심 내용\n\n- 머신러닝\n- 딥러닝",
        "citations": ["https://example.com/paper1", "https://example.com/paper2"],
        "generated_at": "2025-07-29 23:45:00"
    }
    
    result_2 = format_lecture_plan(test_data_2)
    print("테스트 2 결과:")
    print(result_2)
    print()
    
    # 테스트 데이터 3: 빈 데이터
    result_3 = format_lecture_plan(None)
    print("테스트 3 결과 (빈 데이터):")
    print(result_3)
    print()
    
    return True

def test_database_lecture_plans():
    """데이터베이스의 실제 강의안 데이터 확인"""
    print("=== 데이터베이스 강의안 데이터 확인 ===")
    
    try:
        from app import app, db
        from models import Book
        from routes import format_lecture_plan
        
        with app.app_context():
            # 강의안이 있는 책들 확인
            books_with_plans = Book.query.filter(Book.lecture_plan.isnot(None)).limit(3).all()
            
            print(f"강의안이 있는 책 수: {len(books_with_plans)}")
            
            for book in books_with_plans:
                print(f"\n책 ID: {book.id}")
                print(f"제목: {book.title}")
                
                try:
                    # JSON 파싱 테스트
                    lecture_data = json.loads(book.lecture_plan)
                    print(f"강의안 데이터 키: {list(lecture_data.keys())}")
                    
                    # 포맷팅 테스트
                    formatted_content = format_lecture_plan(lecture_data)
                    print(f"포맷팅 결과 길이: {len(formatted_content)} 문자")
                    print(f"포맷팅 미리보기: {formatted_content[:200]}...")
                    
                except json.JSONDecodeError as e:
                    print(f"JSON 파싱 오류: {e}")
                except Exception as e:
                    print(f"포맷팅 오류: {e}")
                    
                print("-" * 50)
                
    except Exception as e:
        print(f"데이터베이스 테스트 오류: {e}")
        return False
    
    return True

def test_perplexity_generator():
    """Perplexity 생성기 기본 테스트"""
    print("=== Perplexity 생성기 테스트 ===")
    
    try:
        from perplexity_generator import PerplexityLectureGenerator
        
        # 생성기 초기화 테스트
        generator = PerplexityLectureGenerator()
        print("✅ Perplexity 생성기 초기화 성공")
        
        # 테스트용 책 데이터
        test_book_data = {
            'title': '테스트 도서',
            'author': '테스트 저자',
            'description': '이것은 테스트용 도서입니다.',
            'contents': '1장: 서론\n2장: 본론\n3장: 결론',
            'pdf_content': ''
        }
        
        test_preferences = {
            'lecture_style': 'comprehensive',
            'target_level': '중급',
            'session_count': '3',
            'session_duration': '90분',
            'special_focus': '실무 중심 교육'
        }
        
        print("테스트 데이터 준비 완료")
        print(f"API 키 설정: {'✅' if generator.api_key else '❌'}")
        
    except Exception as e:
        print(f"Perplexity 생성기 테스트 오류: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("강의안 생성 시스템 단위 테스트 시작\n")
    
    tests = [
        ("포맷팅 함수", test_format_lecture_plan),
        ("데이터베이스 강의안", test_database_lecture_plans),
        ("Perplexity 생성기", test_perplexity_generator)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 {test_name} 테스트 실행...")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"{'✅' if result else '❌'} {test_name} 테스트 {'성공' if result else '실패'}\n")
        except Exception as e:
            print(f"❌ {test_name} 테스트 오류: {e}\n")
            results.append((test_name, False))
    
    # 결과 요약
    print("=" * 60)
    print("테스트 결과 요약:")
    for test_name, result in results:
        print(f"{'✅' if result else '❌'} {test_name}: {'통과' if result else '실패'}")
    
    success_count = sum(1 for _, result in results if result)
    print(f"\n총 {len(results)}개 테스트 중 {success_count}개 성공")