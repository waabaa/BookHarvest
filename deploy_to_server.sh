#!/bin/bash

echo "============================================"
echo "컴북스-AI오투오 서버 배포 스크립트"
echo "aio2o.ktenterprise.net"
echo "============================================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 에러 시 종료
set -e

# 변수 설정
PROJECT_NAME="commbooks-ai"
DOMAIN="aio2o.ktenterprise.net"
PROJECT_DIR="/var/www/$PROJECT_NAME"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="commbooks-ai"
DB_NAME="commbooks_ai"
DB_USER="commbooks_user"

log_info "배포 시작..."

# 1. 필요한 패키지 설치
log_info "필요한 패키지 설치 중..."
apt update
apt install -y python3-dev python3-pip python3-venv build-essential libpq-dev nginx-extras

# 2. 프로젝트 디렉토리 생성
log_info "프로젝트 디렉토리 생성 중..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 3. 가상환경 생성
log_info "Python 가상환경 생성 중..."
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# 4. 프로젝트 파일 업로드 준비 안내
log_warning "이제 다음 파일들을 $PROJECT_DIR 에 업로드해야 합니다:"
echo "  - app.py"
echo "  - routes.py" 
echo "  - models.py"
echo "  - scraper.py"
echo "  - lecture_generator.py"
echo "  - ppt_generator.py"
echo "  - pdf_processor.py"
echo "  - alternative_generators.py"
echo "  - main.py"
echo "  - pyproject.toml"
echo "  - templates/ (전체 폴더)"
echo "  - static/ (전체 폴더)"
echo ""
log_info "파일 업로드 방법:"
echo "1. SCP 사용: scp -r /local/path/* root@$DOMAIN:$PROJECT_DIR/"
echo "2. Git 클론: 추후 Git 저장소 생성 후 사용"
echo "3. FTP/SFTP 클라이언트 사용"
echo ""
read -p "파일 업로드가 완료되었습니까? (y/N): " uploaded
if [[ ! $uploaded =~ ^[Yy]$ ]]; then
    log_error "파일 업로드를 완료한 후 다시 실행해주세요."
    exit 1
fi

# 5. Python 패키지 설치
log_info "Python 패키지 설치 중..."
if [ -f "pyproject.toml" ]; then
    pip install -e .
else
    log_warning "pyproject.toml을 찾을 수 없습니다. 수동으로 패키지를 설치합니다..."
    pip install flask flask-cors flask-sqlalchemy psycopg2-binary gunicorn
    pip install openai anthropic google-genai beautifulsoup4 requests pillow
    pip install trafilatura python-pptx pypdf2 email-validator werkzeug
fi

# 6. PostgreSQL 데이터베이스 설정
log_info "PostgreSQL 데이터베이스 설정 중..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || log_warning "데이터베이스가 이미 존재합니다."
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD 'secure_password_123!';" 2>/dev/null || log_warning "사용자가 이미 존재합니다."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER;"

# 7. 환경 변수 파일 생성
log_info "환경 변수 설정 중..."
cat > $PROJECT_DIR/.env << EOF
# 데이터베이스 설정
DATABASE_URL=postgresql://$DB_USER:secure_password_123!@localhost:5432/$DB_NAME
PGHOST=localhost
PGPORT=5432
PGDATABASE=$DB_NAME
PGUSER=$DB_USER
PGPASSWORD=secure_password_123!

# Flask 설정
SESSION_SECRET=$(openssl rand -hex 32)
FLASK_ENV=production

# API 키들 (나중에 수정 필요)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
EOF

log_warning "환경 변수 파일이 생성되었습니다: $PROJECT_DIR/.env"
log_warning "API 키들을 실제 값으로 수정해주세요!"

# 8. 필요한 디렉토리 생성
log_info "필요한 디렉토리 생성 중..."
mkdir -p $PROJECT_DIR/static/images/covers
mkdir -p $PROJECT_DIR/static/downloads
mkdir -p $PROJECT_DIR/static/css
mkdir -p $PROJECT_DIR/static/js
mkdir -p $PROJECT_DIR/pdfs
chown -R www-data:www-data $PROJECT_DIR/static
chown -R www-data:www-data $PROJECT_DIR/pdfs

# 9. Gunicorn 설정 파일 생성
log_info "Gunicorn 설정 파일 생성 중..."
cat > $PROJECT_DIR/gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
daemon = False
user = "www-data"
group = "www-data"
tmp_upload_dir = None
logfile = "/var/log/commbooks-ai/gunicorn.log"
loglevel = "info"
access_logfile = "/var/log/commbooks-ai/access.log"
error_logfile = "/var/log/commbooks-ai/error.log"
EOF

# 10. 로그 디렉토리 생성
mkdir -p /var/log/commbooks-ai
chown www-data:www-data /var/log/commbooks-ai

# 11. systemd 서비스 파일 생성
log_info "systemd 서비스 생성 중..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=CommBooks AI Flask Application
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$VENV_DIR/bin
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$VENV_DIR/bin/gunicorn --config $PROJECT_DIR/gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 12. Nginx 설정
log_info "Nginx 설정 중..."
cat > /etc/nginx/sites-available/$DOMAIN << EOF
server {
    listen 80;
    server_name $DOMAIN;

    # 보안 헤더
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # 정적 파일 처리
    location /static/ {
        alias $PROJECT_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files \$uri =404;
    }

    # API 엔드포인트 (CORS 헤더 추가)
    location /api/ {
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization" always;
        
        if (\$request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin "*";
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type "text/plain; charset=utf-8";
            add_header Content-Length 0;
            return 204;
        }

        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # 메인 애플리케이션
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # 파일 업로드 크기 제한 (PDF 업로드를 위해)
    client_max_body_size 100M;
}
EOF

# Nginx 사이트 활성화
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 13. 권한 설정
log_info "권한 설정 중..."
chown -R www-data:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
chmod 600 $PROJECT_DIR/.env

# 14. 서비스 시작
log_info "서비스 시작 중..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

# Nginx 재시작
nginx -t && systemctl restart nginx

# 15. SSL 인증서 설치 (Let's Encrypt)
log_info "SSL 인증서 설치 중..."
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect

# 16. 방화벽 설정
log_info "방화벽 설정 중..."
ufw allow 'Nginx Full'
ufw allow OpenSSH
ufw --force enable

# 17. 데이터베이스 초기화
log_info "데이터베이스 초기화 중..."
cd $PROJECT_DIR
source $VENV_DIR/bin/activate
python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('데이터베이스 테이블이 생성되었습니다.')
"

# 18. 서비스 상태 확인
log_info "서비스 상태 확인 중..."
echo "==================== 배포 결과 ===================="
echo "서비스 상태: $(systemctl is-active $SERVICE_NAME)"
echo "Nginx 상태: $(systemctl is-active nginx)"
echo "PostgreSQL 상태: $(systemctl is-active postgresql)"
echo ""
echo "웹사이트 URL: https://$DOMAIN"
echo "API 엔드포인트: https://$DOMAIN/api/"
echo "API 문서: https://$DOMAIN/api_docs"
echo ""
echo "로그 파일:"
echo "  - 애플리케이션: /var/log/commbooks-ai/"
echo "  - Nginx: /var/log/nginx/"
echo "  - systemd: journalctl -u $SERVICE_NAME -f"
echo ""
echo "==================== 중요 알림 ===================="
log_warning "다음 작업을 완료해주세요:"
echo "1. API 키 설정: nano $PROJECT_DIR/.env"
echo "2. 서비스 재시작: systemctl restart $SERVICE_NAME"
echo "3. 로그 확인: journalctl -u $SERVICE_NAME -f"
echo ""
log_success "배포 완료!"

# 19. 관리 스크립트 생성
log_info "관리 스크립트 생성 중..."
cat > /usr/local/bin/commbooks-manage << 'EOF'
#!/bin/bash

PROJECT_DIR="/var/www/commbooks-ai"
SERVICE_NAME="commbooks-ai"

case "$1" in
    start)
        systemctl start $SERVICE_NAME nginx postgresql
        echo "서비스가 시작되었습니다."
        ;;
    stop)
        systemctl stop $SERVICE_NAME
        echo "서비스가 중지되었습니다."
        ;;
    restart)
        systemctl restart $SERVICE_NAME nginx
        echo "서비스가 재시작되었습니다."
        ;;
    status)
        echo "=== 서비스 상태 ==="
        echo "CommBooks AI: $(systemctl is-active $SERVICE_NAME)"
        echo "Nginx: $(systemctl is-active nginx)"
        echo "PostgreSQL: $(systemctl is-active postgresql)"
        echo ""
        echo "=== 최근 로그 ==="
        journalctl -u $SERVICE_NAME --no-pager -n 10
        ;;
    logs)
        journalctl -u $SERVICE_NAME -f
        ;;
    update)
        cd $PROJECT_DIR
        source venv/bin/activate
        git pull
        pip install -e .
        systemctl restart $SERVICE_NAME
        echo "업데이트 완료"
        ;;
    backup)
        pg_dump commbooks_ai > "/tmp/commbooks_backup_$(date +%Y%m%d_%H%M%S).sql"
        tar -czf "/tmp/commbooks_files_$(date +%Y%m%d_%H%M%S).tar.gz" -C /var/www commbooks-ai
        echo "백업 완료: /tmp/"
        ;;
    *)
        echo "사용법: $0 {start|stop|restart|status|logs|update|backup}"
        exit 1
        ;;
esac
EOF

chmod +x /usr/local/bin/commbooks-manage

log_success "관리 스크립트가 생성되었습니다: commbooks-manage"
echo "사용법: commbooks-manage {start|stop|restart|status|logs|update|backup}"

log_success "모든 배포 작업이 완료되었습니다!"