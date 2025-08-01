#!/bin/bash

echo "============================================"
echo "프로젝트 파일 패키징 스크립트"
echo "서버 업로드용 파일 생성"
echo "============================================"

# 패키지 디렉토리 생성
PACKAGE_DIR="commbooks-ai-package"
rm -rf $PACKAGE_DIR
mkdir -p $PACKAGE_DIR

echo "📦 필요한 파일들을 패키징 중..."

# Python 파일들 복사
cp app.py $PACKAGE_DIR/
cp routes.py $PACKAGE_DIR/
cp models.py $PACKAGE_DIR/
cp scraper.py $PACKAGE_DIR/
cp lecture_generator.py $PACKAGE_DIR/
cp ppt_generator.py $PACKAGE_DIR/
cp pdf_processor.py $PACKAGE_DIR/
cp alternative_generators.py $PACKAGE_DIR/
cp main.py $PACKAGE_DIR/
cp pyproject.toml $PACKAGE_DIR/

# 템플릿 폴더 복사
cp -r templates $PACKAGE_DIR/

# 스태틱 폴더 복사 (이미지 제외)
mkdir -p $PACKAGE_DIR/static/css
mkdir -p $PACKAGE_DIR/static/js
mkdir -p $PACKAGE_DIR/static/images/covers
mkdir -p $PACKAGE_DIR/static/downloads

# CSS 파일이 있다면 복사
if [ -d "static/css" ]; then
    cp -r static/css/* $PACKAGE_DIR/static/css/ 2>/dev/null || true
fi

# README 파일 생성
cat > $PACKAGE_DIR/README.md << 'EOF'
# CommBooks AI 서버 배포 가이드

## 1. 파일 업로드
이 폴더의 모든 파일을 서버의 `/var/www/commbooks-ai/` 디렉토리에 업로드하세요.

```bash
# SCP로 업로드 (로컬에서 실행)
scp -r * root@aio2o.ktenterprise.net:/var/www/commbooks-ai/

# 또는 서버에서 직접 다운로드
wget [파일_URL] -O commbooks-ai-package.tar.gz
tar -xzf commbooks-ai-package.tar.gz
mv commbooks-ai-package/* /var/www/commbooks-ai/
```

## 2. 권한 설정
```bash
chown -R www-data:www-data /var/www/commbooks-ai
chmod -R 755 /var/www/commbooks-ai
```

## 3. API 키 설정
`.env` 파일을 편집하여 실제 API 키를 입력하세요:

```bash
nano /var/www/commbooks-ai/.env
```

다음 값들을 수정하세요:
- OPENAI_API_KEY=실제_OpenAI_키
- ANTHROPIC_API_KEY=실제_Anthropic_키 (선택사항)
- GEMINI_API_KEY=실제_Gemini_키 (선택사항)

## 4. 서비스 재시작
```bash
systemctl restart commbooks-ai
```

## 5. 관리 명령어
```bash
# 상태 확인
commbooks-manage status

# 로그 확인
commbooks-manage logs

# 서비스 재시작
commbooks-manage restart
```
EOF

# 압축 파일 생성
tar -czf commbooks-ai-package.tar.gz $PACKAGE_DIR

echo "✅ 패키징 완료!"
echo ""
echo "생성된 파일들:"
echo "  - commbooks-ai-package/ (폴더)"
echo "  - commbooks-ai-package.tar.gz (압축파일)"
echo ""
echo "📡 서버 업로드 방법:"
echo "1. SCP 사용:"
echo "   scp commbooks-ai-package.tar.gz root@aio2o.ktenterprise.net:~/"
echo ""
echo "2. 서버에서 압축 해제:"
echo "   tar -xzf commbooks-ai-package.tar.gz"
echo "   cp -r commbooks-ai-package/* /var/www/commbooks-ai/"
echo ""
echo "3. 권한 설정:"
echo "   chown -R www-data:www-data /var/www/commbooks-ai"