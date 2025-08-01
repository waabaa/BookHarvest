#!/bin/bash

echo "============================================"
echo "서버 환경 체크 스크립트"
echo "aio2o.ktenterprise.net 배포 준비"
echo "============================================"
echo

# 시스템 정보
echo "📋 시스템 정보"
echo "----------------------------------------"
echo "OS: $(lsb_release -d 2>/dev/null | cut -f2 || cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "커널: $(uname -r)"
echo "아키텍처: $(uname -m)"
echo "호스트명: $(hostname)"
echo "사용자: $(whoami)"
echo "현재 디렉토리: $(pwd)"
echo

# 네트워크 정보
echo "🌐 네트워크 정보"
echo "----------------------------------------"
echo "외부 IP: $(curl -s ifconfig.me 2>/dev/null || echo '확인 불가')"
echo "내부 IP: $(hostname -I | awk '{print $1}' 2>/dev/null || echo '확인 불가')"
echo "도메인 확인: $(nslookup aio2o.ktenterprise.net 2>/dev/null | grep -A1 'Name:' | tail -1 | awk '{print $2}' || echo '확인 불가')"
echo

# 권한 확인
echo "🔐 권한 확인"
echo "----------------------------------------"
if [ "$EUID" -eq 0 ]; then
    echo "Root 권한: ✅ root 사용자로 실행 중"
else
    echo "Root 권한: $(sudo -n true 2>/dev/null && echo '✅ sudo 권한 있음' || echo '❌ sudo 권한 없음')"
fi
echo

# Python 환경
echo "🐍 Python 환경"
echo "----------------------------------------"
python3_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 || echo '미설치')
echo "Python3 버전: $python3_version"
pip3_version=$(pip3 --version 2>/dev/null | cut -d' ' -f2 || echo '미설치')
echo "pip3 버전: $pip3_version"
if command -v python3 >/dev/null 2>&1; then
    echo "Python3 경로: $(which python3)"
    echo "Python 패키지 설치 위치: $(python3 -c 'import site; print(site.getsitepackages()[0])' 2>/dev/null || echo '확인 불가')"
else
    echo "❌ Python3가 설치되지 않음"
fi
echo

# 가상환경 도구
echo "📦 가상환경 도구"
echo "----------------------------------------"
echo "venv: $(python3 -m venv --help >/dev/null 2>&1 && echo '✅ 사용 가능' || echo '❌ 사용 불가')"
echo "virtualenv: $(command -v virtualenv >/dev/null 2>&1 && echo '✅ 설치됨' || echo '❌ 미설치')"
echo

# 데이터베이스
echo "🗄️ 데이터베이스"
echo "----------------------------------------"
# PostgreSQL 확인
if command -v psql >/dev/null 2>&1; then
    pg_version=$(psql --version | cut -d' ' -f3)
    echo "PostgreSQL: ✅ 설치됨 (버전: $pg_version)"
    echo "PostgreSQL 서비스 상태: $(systemctl is-active postgresql 2>/dev/null || echo '확인 불가')"
    echo "PostgreSQL 포트: $(sudo netstat -tlnp 2>/dev/null | grep :5432 | awk '{print $4}' || echo '5432 포트 미사용')"
else
    echo "PostgreSQL: ❌ 미설치"
fi

# MySQL 확인
if command -v mysql >/dev/null 2>&1; then
    mysql_version=$(mysql --version | cut -d' ' -f6 | cut -d',' -f1)
    echo "MySQL: ✅ 설치됨 (버전: $mysql_version)"
    echo "MySQL 서비스 상태: $(systemctl is-active mysql 2>/dev/null || echo '확인 불가')"
else
    echo "MySQL: ❌ 미설치"
fi

# SQLite 확인
if command -v sqlite3 >/dev/null 2>&1; then
    sqlite_version=$(sqlite3 --version | cut -d' ' -f1)
    echo "SQLite: ✅ 설치됨 (버전: $sqlite_version)"
else
    echo "SQLite: ❌ 미설치"
fi
echo

# 웹서버
echo "🌍 웹서버"
echo "----------------------------------------"
# Nginx 확인
if command -v nginx >/dev/null 2>&1; then
    nginx_version=$(nginx -v 2>&1 | cut -d'/' -f2)
    echo "Nginx: ✅ 설치됨 (버전: $nginx_version)"
    echo "Nginx 서비스 상태: $(systemctl is-active nginx 2>/dev/null || echo '확인 불가')"
    echo "Nginx 설정 파일: $(nginx -t 2>&1 | grep 'syntax is ok' >/dev/null && echo '✅ 정상' || echo '❌ 문제 있음')"
else
    echo "Nginx: ❌ 미설치"
fi

# Apache 확인
if command -v apache2 >/dev/null 2>&1 || command -v httpd >/dev/null 2>&1; then
    apache_cmd=$(command -v apache2 2>/dev/null || command -v httpd)
    apache_version=$($apache_cmd -v 2>/dev/null | head -1 | cut -d' ' -f3)
    echo "Apache: ✅ 설치됨 (버전: $apache_version)"
    service_name=$(systemctl list-units --type=service | grep -E "(apache2|httpd)" | awk '{print $1}' | head -1)
    if [ -n "$service_name" ]; then
        echo "Apache 서비스 상태: $(systemctl is-active $service_name 2>/dev/null || echo '확인 불가')"
    fi
else
    echo "Apache: ❌ 미설치"
fi
echo

# 포트 사용 현황
echo "🔌 포트 사용 현황"
echo "----------------------------------------"
echo "포트 80 (HTTP): $(sudo netstat -tlnp 2>/dev/null | grep :80 | awk '{print $1, $4}' || echo '사용 안함')"
echo "포트 443 (HTTPS): $(sudo netstat -tlnp 2>/dev/null | grep :443 | awk '{print $1, $4}' || echo '사용 안함')"
echo "포트 5000 (Flask): $(sudo netstat -tlnp 2>/dev/null | grep :5000 | awk '{print $1, $4}' || echo '사용 안함')"
echo "포트 8000 (일반): $(sudo netstat -tlnp 2>/dev/null | grep :8000 | awk '{print $1, $4}' || echo '사용 안함')"
echo

# Git 확인
echo "📚 Git"
echo "----------------------------------------"
if command -v git >/dev/null 2>&1; then
    git_version=$(git --version | cut -d' ' -f3)
    echo "Git: ✅ 설치됨 (버전: $git_version)"
    echo "Git 사용자: $(git config --global user.name 2>/dev/null || echo '미설정')"
    echo "Git 이메일: $(git config --global user.email 2>/dev/null || echo '미설정')"
else
    echo "Git: ❌ 미설치"
fi
echo

# 디스크 용량
echo "💾 디스크 용량"
echo "----------------------------------------"
df -h / | tail -1 | while read filesystem size used avail use_percent mount; do
    echo "전체 용량: $size"
    echo "사용 용량: $used"
    echo "여유 용량: $avail"
    echo "사용률: $use_percent"
done
echo

# 메모리 정보
echo "🧠 메모리 정보"
echo "----------------------------------------"
total_mem=$(free -h | grep 'Mem:' | awk '{print $2}')
used_mem=$(free -h | grep 'Mem:' | awk '{print $3}')
free_mem=$(free -h | grep 'Mem:' | awk '{print $4}')
echo "전체 메모리: $total_mem"
echo "사용 메모리: $used_mem"
echo "여유 메모리: $free_mem"
echo

# 프로세스 관리 도구
echo "⚙️ 프로세스 관리 도구"
echo "----------------------------------------"
echo "systemd: $(command -v systemctl >/dev/null 2>&1 && echo '✅ 사용 가능' || echo '❌ 사용 불가')"
echo "PM2: $(command -v pm2 >/dev/null 2>&1 && echo '✅ 설치됨' || echo '❌ 미설치')"
echo "supervisor: $(command -v supervisord >/dev/null 2>&1 && echo '✅ 설치됨' || echo '❌ 미설치')"
echo

# SSL/인증서 도구
echo "🔒 SSL/인증서 도구"
echo "----------------------------------------"
echo "OpenSSL: $(openssl version 2>/dev/null || echo '❌ 미설치')"
echo "Certbot: $(command -v certbot >/dev/null 2>&1 && echo '✅ 설치됨' || echo '❌ 미설치')"
echo

# 방화벽 확인
echo "🛡️ 방화벽 상태"
echo "----------------------------------------"
echo "UFW 상태: $(sudo ufw status 2>/dev/null | head -1 || echo '확인 불가')"
echo "iptables 규칙 수: $(sudo iptables -L 2>/dev/null | wc -l || echo '확인 불가')"
echo

# 환경 변수 확인
echo "🔧 주요 환경 변수"
echo "----------------------------------------"
echo "PATH: ${PATH:0:100}..."
echo "HOME: $HOME"
echo "USER: $USER"
echo "SHELL: $SHELL"
echo

# 추천 설치 패키지
echo "📋 배포를 위한 추천 설치 명령어"
echo "----------------------------------------"
echo "# 기본 패키지 업데이트"
echo "sudo apt update && sudo apt upgrade -y"
echo
echo "# Python 및 필수 도구"
echo "sudo apt install -y python3 python3-pip python3-venv python3-dev"
echo
echo "# PostgreSQL 설치"
echo "sudo apt install -y postgresql postgresql-contrib"
echo
echo "# Nginx 설치"
echo "sudo apt install -y nginx"
echo
echo "# Git 설치"
echo "sudo apt install -y git"
echo
echo "# SSL 인증서 도구"
echo "sudo apt install -y certbot python3-certbot-nginx"
echo
echo "# 기타 유용한 도구"
echo "sudo apt install -y curl wget unzip htop tree"
echo

echo "============================================"
echo "체크 완료! 이 결과를 개발자에게 전달해주세요."
echo "============================================"