#!/bin/bash

echo "========================================"
echo "설정 파일 초기화"
echo "========================================"
echo ""

echo "[1/3] 기존 설정 파일 삭제..."
if [ -f config/config.json ]; then
    rm config/config.json
    echo "기존 설정 파일 삭제됨"
else
    echo "설정 파일이 없습니다"
fi

echo ""
echo "[2/3] 모델 설정 실행..."
python setup_models.py

echo ""
echo "[3/3] 시스템 테스트..."
python test_system.py

echo ""
echo "========================================"
echo "설정 초기화 완료!"
echo ""
echo "이제 실행하세요:"
echo "streamlit run app.py"
echo "========================================"