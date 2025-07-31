# 컴북스-AI오투오 웹사이트 이전 가이드

## 개요
이 문서는 컴북스-AI오투오 AI 강의안 생성 시스템을 새로운 서버나 호스팅 환경으로 이전하는 방법을 설명합니다.

## 시스템 요구사항

### 최소 시스템 요구사항
- **Python**: 3.8 이상
- **데이터베이스**: PostgreSQL 12 이상
- **메모리**: 최소 2GB RAM (권장 4GB)
- **저장공간**: 최소 10GB (이미지 및 PDF 저장용)
- **네트워크**: 안정적인 인터넷 연결 (AI API 호출용)

### 환경 변수 설정
다음 환경 변수들이 필요합니다:

```bash
# 데이터베이스 설정
DATABASE_URL=postgresql://username:password@host:port/database_name
PGHOST=your_postgres_host
PGPORT=5432
PGUSER=your_postgres_user
PGPASSWORD=your_postgres_password
PGDATABASE=your_database_name

# AI API 키들
OPENAI_API_KEY=your_openai_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key

# 보안 설정
SESSION_SECRET=your_secret_key_for_sessions
```

## 이전 단계

### 1. 데이터 백업
현재 시스템에서 다음 데이터를 백업하세요:

#### 데이터베이스 백업
```bash
# PostgreSQL 데이터베이스 전체 백업
pg_dump -h your_host -U your_user -d your_database > commbooks_backup.sql

# 또는 커스텀 포맷으로
pg_dump -h your_host -U your_user -Fc -d your_database > commbooks_backup.dump
```

#### 파일 시스템 백업
```bash
# static 폴더 전체 백업 (책 표지, 저자 사진, PDF 등)
tar -czf static_files_backup.tar.gz static/

# 애플리케이션 코드 백업
tar -czf application_backup.tar.gz --exclude=static --exclude=__pycache__ .
```

### 2. 새 환경 준비

#### Python 환경 설정
```bash
# Python 가상환경 생성
python3 -m venv commbooks_env
source commbooks_env/bin/activate  # Linux/Mac
# 또는 commbooks_env\Scripts\activate  # Windows

# 필요 패키지 설치
pip install -r requirements.txt
```

#### 데이터베이스 설정
```bash
# PostgreSQL 설치 (Ubuntu 예시)
sudo apt update
sudo apt install postgresql postgresql-contrib

# 데이터베이스 사용자 및 데이터베이스 생성
sudo -u postgres createuser --interactive commbooks_user
sudo -u postgres createdb commbooks_db -O commbooks_user
```

### 3. 데이터 복원

#### 데이터베이스 복원
```bash
# SQL 파일로 복원
psql -h new_host -U commbooks_user -d commbooks_db < commbooks_backup.sql

# 또는 커스텀 포맷으로 복원
pg_restore -h new_host -U commbooks_user -d commbooks_db commbooks_backup.dump
```

#### 파일 복원
```bash
# static 폴더 복원
tar -xzf static_files_backup.tar.gz

# 권한 설정
chmod -R 755 static/
```

### 4. 애플리케이션 설정

#### 환경 변수 설정
```bash
# .env 파일 생성
cat > .env << EOF
DATABASE_URL=postgresql://commbooks_user:password@localhost:5432/commbooks_db
OPENAI_API_KEY=your_openai_key
PERPLEXITY_API_KEY=your_perplexity_key
SESSION_SECRET=your_secret_key
EOF
```

#### 데이터베이스 마이그레이션 확인
```bash
# 애플리케이션 실행하여 테이블 생성 확인
python main.py
```

### 5. 웹 서버 설정

#### Nginx 설정 (권장)
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/app/static/;
        expires 30d;
    }

    client_max_body_size 100M;  # PDF 업로드용
}
```

#### Systemd 서비스 설정 (Linux)
```ini
[Unit]
Description=CommBooks AI Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/app/commbooks_env/bin
ExecStart=/path/to/your/app/commbooks_env/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 6. SSL 인증서 설정 (HTTPS)
```bash
# Let's Encrypt 사용 (권장)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

## 이전 후 확인사항

### 기능 테스트 체크리스트
- [ ] 웹사이트 접속 확인
- [ ] 기존 도서 데이터 표시 확인
- [ ] 새로운 스크래핑 작업 실행 테스트
- [ ] AI 강의안 생성 테스트
- [ ] PDF 업로드 및 다운로드 테스트
- [ ] 데이터 내보내기 기능 테스트
- [ ] 저자 사진 자동 추출 확인

### 성능 최적화
```bash
# 데이터베이스 인덱스 확인
psql -d commbooks_db -c "SELECT schemaname, tablename, indexname FROM pg_indexes WHERE schemaname = 'public';"

# 로그 설정 확인
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## 백업 스케줄 설정

### 자동 백업 스크립트
```bash
#!/bin/bash
# backup_commbooks.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/commbooks"

# 데이터베이스 백업
pg_dump -h localhost -U commbooks_user -Fc commbooks_db > $BACKUP_DIR/db_backup_$DATE.dump

# 파일 백업
tar -czf $BACKUP_DIR/static_backup_$DATE.tar.gz static/

# 7일 이상 된 백업 파일 삭제
find $BACKUP_DIR -name "*.dump" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### Crontab 설정
```bash
# 매일 새벽 2시에 백업 실행
0 2 * * * /path/to/backup_commbooks.sh
```

## 문제 해결

### 일반적인 문제들

#### 1. 데이터베이스 연결 오류
```bash
# PostgreSQL 서비스 상태 확인
sudo systemctl status postgresql

# 연결 테스트
psql -h localhost -U commbooks_user -d commbooks_db -c "SELECT 1;"
```

#### 2. AI API 연결 오류
- API 키 확인
- 네트워크 연결 상태 확인
- API 사용량 한도 확인

#### 3. 파일 권한 오류
```bash
# 적절한 권한 설정
sudo chown -R www-data:www-data /path/to/app/
sudo chmod -R 755 /path/to/app/static/
```

#### 4. 메모리 부족
- Gunicorn worker 수 조정
- 시스템 메모리 모니터링
- 필요시 스왑 공간 추가

### 로그 확인
```bash
# 애플리케이션 로그
journalctl -u commbooks-app -f

# Nginx 로그
tail -f /var/log/nginx/error.log

# PostgreSQL 로그
tail -f /var/log/postgresql/postgresql-*.log
```

## 보안 고려사항

### 필수 보안 설정
1. **방화벽 설정**: 필요한 포트만 개방
2. **데이터베이스 보안**: 외부 접근 제한
3. **API 키 보안**: 환경 변수로만 관리
4. **정기적인 업데이트**: 시스템 및 패키지 업데이트
5. **HTTPS 강제**: SSL 인증서 적용

### 권장 보안 도구
- **Fail2ban**: 브루트 포스 공격 방지
- **UFW**: 간편한 방화벽 관리
- **Logwatch**: 로그 모니터링

## 연락처 및 지원

시스템 이전 과정에서 문제가 발생하면 다음을 확인하세요:
1. 이 가이드의 문제 해결 섹션
2. 애플리케이션 로그 파일
3. 각 구성 요소의 공식 문서

---
*이 가이드는 컴북스-AI오투오 시스템 v1.0 기준으로 작성되었습니다.*
*마지막 업데이트: 2025-07-31*