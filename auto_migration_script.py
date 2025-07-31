#!/usr/bin/env python3
"""
Korean Language Tutor 자동 통합 스크립트
이 스크립트를 Korean Language Tutor 프로젝트에서 실행하면 CommBooks 기능이 자동으로 통합됩니다.
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

def print_step(step, description):
    print(f"\n{'='*50}")
    print(f"STEP {step}: {description}")
    print(f"{'='*50}")

def run_command(command, description=""):
    """명령어 실행 및 결과 확인"""
    print(f"실행 중: {command}")
    if description:
        print(f"설명: {description}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"오류 발생: {result.stderr}")
        return False
    else:
        print(f"성공: {result.stdout}")
        return True

def check_file_exists(filepath):
    """파일 존재 확인"""
    if os.path.exists(filepath):
        print(f"✓ {filepath} 파일이 존재합니다.")
        return True
    else:
        print(f"✗ {filepath} 파일이 없습니다.")
        return False

def backup_existing_files():
    """기존 파일 백업"""
    backup_files = ['models.py', 'routes.py', 'templates/base.html']
    backup_dir = 'backup_before_commbooks'
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    for file in backup_files:
        if os.path.exists(file):
            shutil.copy2(file, f"{backup_dir}/{os.path.basename(file)}.backup")
            print(f"백업 완료: {file}")

def download_commbooks_package():
    """CommBooks 통합 패키지 다운로드"""
    print_step(1, "CommBooks 통합 패키지 다운로드")
    
    # 사용자가 업로드한 파일들이 있는지 확인
    required_files = [
        'korean_tutor_integration_package.tar.gz',
        'commbooks_data_backup.sql',
        'commbooks_images.tar.gz'
    ]
    
    missing_files = []
    for file in required_files:
        if not check_file_exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"다음 파일들을 Korean Language Tutor 프로젝트에 업로드해주세요:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    return True

def extract_packages():
    """패키지 압축 해제"""
    print_step(2, "패키지 압축 해제")
    
    # 메인 통합 패키지 압축 해제
    if not run_command("tar -xzf korean_tutor_integration_package.tar.gz", "통합 패키지 압축 해제"):
        return False
    
    # 이미지 파일 압축 해제
    if os.path.exists('commbooks_images.tar.gz'):
        if not run_command("tar -xzf commbooks_images.tar.gz", "이미지 파일 압축 해제"):
            return False
    
    return True

def install_packages():
    """필요한 패키지 설치"""
    print_step(3, "Python 패키지 설치")
    
    packages = [
        'beautifulsoup4==4.12.2',
        'requests==2.31.0',
        'pillow==10.0.0',
        'openai==1.0.0',
        'anthropic==0.5.0',
        'google-genai==0.5.0',
        'trafilatura==1.6.0',
        'pypdf2==3.0.0',
        'python-pptx==0.6.21',
        'psycopg2-binary==2.9.0'
    ]
    
    for package in packages:
        if not run_command(f"pip install {package}", f"{package} 설치"):
            print(f"경고: {package} 설치 실패")
    
    return True

def copy_python_modules():
    """Python 모듈 파일들 복사"""
    print_step(4, "Python 모듈 통합")
    
    source_dir = 'migration_to_korean_tutor/python_modules'
    if not os.path.exists(source_dir):
        print(f"오류: {source_dir} 폴더가 없습니다.")
        return False
    
    # Python 파일들 복사
    for file in os.listdir(source_dir):
        if file.endswith('.py'):
            shutil.copy2(f"{source_dir}/{file}", file)
            print(f"복사됨: {file}")
    
    return True

def integrate_templates():
    """템플릿 파일 통합"""
    print_step(5, "템플릿 파일 통합")
    
    source_templates = 'migration_to_korean_tutor/templates'
    target_templates = 'templates'
    
    if not os.path.exists(source_templates):
        print(f"오류: {source_templates} 폴더가 없습니다.")
        return False
    
    # CommBooks 전용 템플릿 폴더 생성
    commbooks_template_dir = f"{target_templates}/commbooks"
    if not os.path.exists(commbooks_template_dir):
        os.makedirs(commbooks_template_dir)
    
    # CommBooks 템플릿 파일들 복사
    commbooks_files = ['dashboard.html', 'book_detail.html', 'books_list.html', 'jobs_list.html']
    for file in commbooks_files:
        source_file = f"{source_templates}/{file}"
        if os.path.exists(source_file):
            shutil.copy2(source_file, f"{commbooks_template_dir}/{file}")
            print(f"CommBooks 템플릿 복사됨: {file}")
    
    return True

def update_models():
    """모델 파일 업데이트"""
    print_step(6, "데이터베이스 모델 통합")
    
    # 기존 models.py 백업
    if os.path.exists('models.py'):
        shutil.copy2('models.py', 'models_original.py.backup')
    
    # CommBooks 모델을 기존 models.py에 추가
    commbooks_models = """

# CommBooks 통합 모델들
from datetime import datetime
import json

class Book(db.Model):
    __tablename__ = 'commbooks_books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(200))
    publisher = db.Column(db.String(200))
    publish_date = db.Column(db.String(50))
    description = db.Column(db.Text)
    table_of_contents = db.Column(db.Text)
    book_preview = db.Column(db.Text)
    cover_image_path = db.Column(db.String(500))
    source_url = db.Column(db.String(1000), unique=True)
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # AI 강의안 관련
    lecture_plan = db.Column(db.Text)  # JSON 형태로 저장
    
    # 저자 사진 관련
    author_photo_path = db.Column(db.String(500))
    author_photo_rounded_path = db.Column(db.String(500))
    
    # PDF 관련
    pdf_file_path = db.Column(db.String(500))
    pdf_content = db.Column(db.Text)
    
    # 시리즈 정보
    series_name = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Book {self.title}>'

class ScrapingJob(db.Model):
    __tablename__ = 'commbooks_scraping_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    start_page = db.Column(db.Integer, nullable=False)
    end_page = db.Column(db.Integer, nullable=False)
    current_page = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    
    # 진행 상황
    total_books_found = db.Column(db.Integer, default=0)
    books_scraped = db.Column(db.Integer, default=0)
    books_failed = db.Column(db.Integer, default=0)
    
    # 시간 정보
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # 에러 정보
    error_message = db.Column(db.Text)
    
    # 시리즈 정보
    series_name = db.Column(db.String(200))
    series_url = db.Column(db.String(1000))
    
    def __repr__(self):
        return f'<ScrapingJob {self.start_page}-{self.end_page}>'
"""
    
    try:
        with open('models.py', 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # CommBooks 모델이 이미 있는지 확인
        if 'commbooks_books' not in existing_content:
            with open('models.py', 'a', encoding='utf-8') as f:
                f.write(commbooks_models)
            print("CommBooks 모델이 추가되었습니다.")
        else:
            print("CommBooks 모델이 이미 존재합니다.")
        
        return True
    except Exception as e:
        print(f"모델 업데이트 오류: {e}")
        return False

def update_routes():
    """라우트 파일 업데이트"""
    print_step(7, "라우트 통합")
    
    # 기존 routes.py 백업
    if os.path.exists('routes.py'):
        shutil.copy2('routes.py', 'routes_original.py.backup')
    
    # CommBooks 라우트 추가
    routes_file = 'migration_to_korean_tutor/routes_to_add.py'
    if not os.path.exists(routes_file):
        print(f"오류: {routes_file}이 없습니다.")
        return False
    
    try:
        with open('routes.py', 'r', encoding='utf-8') as f:
            existing_routes = f.read()
        
        with open(routes_file, 'r', encoding='utf-8') as f:
            new_routes = f.read()
        
        # CommBooks 라우트가 이미 있는지 확인
        if '/commbooks' not in existing_routes:
            # import 구문들 추가
            import_statements = """
# CommBooks 통합을 위한 추가 import
from models import Book, ScrapingJob
from scraper import CommBooksScraper
from lecture_generator import LectureGenerator
from perplexity_generator import PerplexityLectureGenerator
from image_processor import ImageProcessor
import threading
import json
"""
            
            # 파일 끝에 라우트 추가
            with open('routes.py', 'a', encoding='utf-8') as f:
                f.write(import_statements)
                f.write(new_routes)
            
            print("CommBooks 라우트가 추가되었습니다.")
        else:
            print("CommBooks 라우트가 이미 존재합니다.")
        
        return True
    except Exception as e:
        print(f"라우트 업데이트 오류: {e}")
        return False

def restore_database():
    """데이터베이스 복원"""
    print_step(8, "데이터베이스 복원")
    
    if not os.path.exists('commbooks_data_backup.sql'):
        print("데이터베이스 백업 파일이 없습니다. 빈 테이블로 시작합니다.")
        return True
    
    # 테이블 생성
    if not run_command("python -c \"from app import app, db; app.app_context().push(); db.create_all()\"", "테이블 생성"):
        print("경고: 테이블 생성 실패")
    
    # 데이터 복원
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if run_command(f"psql '{database_url}' < commbooks_data_backup.sql", "데이터베이스 복원"):
            print("데이터베이스 복원 완료")
        else:
            print("경고: 데이터베이스 복원 실패")
    else:
        print("경고: DATABASE_URL 환경 변수가 설정되지 않았습니다.")
    
    return True

def update_navigation():
    """네비게이션 메뉴 업데이트"""
    print_step(9, "네비게이션 메뉴 업데이트")
    
    base_template = 'templates/base.html'
    if not os.path.exists(base_template):
        print(f"경고: {base_template}을 찾을 수 없습니다.")
        return True
    
    try:
        with open(base_template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # CommBooks 메뉴가 이미 있는지 확인
        if '/commbooks' not in content:
            # 네비게이션 메뉴 추가
            commbooks_nav = '''
                <li class="nav-item">
                    <a class="nav-link" href="/commbooks">📚 도서 관리</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/commbooks/books">📖 책 목록</a>
                </li>'''
            
            # </ul> 태그 앞에 추가
            content = content.replace('</ul>', f'{commbooks_nav}\n                </ul>')
            
            with open(base_template, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("네비게이션 메뉴가 업데이트되었습니다.")
        else:
            print("CommBooks 메뉴가 이미 존재합니다.")
        
        return True
    except Exception as e:
        print(f"네비게이션 업데이트 오류: {e}")
        return False

def setup_environment():
    """환경 변수 설정 안내"""
    print_step(10, "환경 변수 설정")
    
    required_secrets = [
        'OPENAI_API_KEY',
        'PERPLEXITY_API_KEY',
        'ANTHROPIC_API_KEY',  # 선택사항
        'GEMINI_API_KEY'      # 선택사항
    ]
    
    print("다음 환경 변수들을 Replit Secrets에 설정해주세요:")
    for secret in required_secrets:
        print(f"  - {secret}")
    
    print("\n설정 방법:")
    print("1. Replit 좌측 사이드바에서 'Secrets' 클릭")
    print("2. 위의 API 키들을 각각 추가")
    print("3. 값은 해당 서비스에서 발급받은 API 키 입력")
    
    return True

def run_tests():
    """통합 테스트 실행"""
    print_step(11, "통합 테스트")
    
    print("다음 URL들에 접속하여 정상 작동을 확인하세요:")
    print("  - /commbooks - CommBooks 대시보드")
    print("  - /commbooks/books - 책 목록")
    print("  - /authors - 기존 강사진 페이지")
    print("  - /curriculums - 기존 교육과정 페이지")
    
    return True

def main():
    """메인 통합 프로세스"""
    print("🚀 Korean Language Tutor + CommBooks 통합 시작!")
    print("이 스크립트는 CommBooks 기능을 Korean Language Tutor에 자동으로 통합합니다.")
    
    # 백업
    backup_existing_files()
    
    # 단계별 실행
    steps = [
        (download_commbooks_package, "통합 패키지 확인"),
        (extract_packages, "패키지 압축 해제"),
        (install_packages, "Python 패키지 설치"),
        (copy_python_modules, "Python 모듈 복사"),
        (integrate_templates, "템플릿 통합"),
        (update_models, "데이터베이스 모델 업데이트"),
        (update_routes, "라우트 통합"),
        (restore_database, "데이터베이스 복원"),
        (update_navigation, "네비게이션 업데이트"),
        (setup_environment, "환경 변수 설정"),
        (run_tests, "테스트 안내")
    ]
    
    failed_steps = []
    
    for i, (func, description) in enumerate(steps, 1):
        try:
            if not func():
                failed_steps.append(f"Step {i}: {description}")
        except Exception as e:
            print(f"Step {i} 오류: {e}")
            failed_steps.append(f"Step {i}: {description} (오류: {e})")
    
    # 결과 보고
    print("\n" + "="*60)
    print("🎉 통합 프로세스 완료!")
    print("="*60)
    
    if failed_steps:
        print("⚠️  다음 단계들에서 문제가 발생했습니다:")
        for step in failed_steps:
            print(f"   {step}")
        print("\n수동으로 해결하거나 다시 실행해주세요.")
    else:
        print("✅ 모든 단계가 성공적으로 완료되었습니다!")
    
    print("\n다음 단계:")
    print("1. Replit을 재시작하세요")
    print("2. /commbooks 경로로 접속하여 동작 확인")
    print("3. API 키들이 제대로 설정되었는지 확인")
    print("4. 스크래핑 테스트 실행")
    
    print("\n🎯 통합 완료! Korean Language Tutor에서 CommBooks 기능을 사용할 수 있습니다!")

if __name__ == "__main__":
    main()