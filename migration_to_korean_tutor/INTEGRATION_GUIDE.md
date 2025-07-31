
# Korean Language Tutor 통합 가이드

## 1. 파일 배치
1. `python_modules/` 폴더의 모든 파일을 Korean Language Tutor 프로젝트 루트에 복사
2. `templates/` 폴더를 Korean Language Tutor의 templates 폴더에 병합
3. `routes_to_add.py`의 내용을 Korean Language Tutor의 routes.py에 추가

## 2. 패키지 설치
`config_additions.txt`에 있는 패키지들을 pyproject.toml에 추가하고 설치

## 3. 환경 변수 설정
Replit Secrets에 API 키들 추가

## 4. 데이터베이스 마이그레이션
1. `commbooks_data_backup.sql` 파일을 Korean Language Tutor 프로젝트에 업로드
2. PostgreSQL에 데이터 복원:
   ```bash
   psql $DATABASE_URL < commbooks_data_backup.sql
   ```

## 5. 이미지 파일 복원
1. `commbooks_images.tar.gz` 파일을 Korean Language Tutor 프로젝트에 업로드
2. 압축 해제:
   ```bash
   tar -xzf commbooks_images.tar.gz
   ```

## 6. 네비게이션 메뉴 추가
base.html 또는 main layout에 CommBooks 메뉴 추가:
```html
<li><a href="/commbooks">도서 관리</a></li>
<li><a href="/commbooks/books">책 목록</a></li>
```

## 7. 테스트
- /commbooks 경로로 접속하여 대시보드 확인
- 스크래핑 기능 테스트
- 강의안 생성 기능 테스트
