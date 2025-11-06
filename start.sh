#!/bin/bash

echo "========================================"
echo "mem0 LTM 시스템 시작"
echo "========================================"
echo ""

echo "[1/3] 가상환경 활성화 중..."
source venv/bin/activate

echo ""
echo "[2/3] Ollama 서비스 확인 중..."
if ! ollama list &> /dev/null; then
    echo "Ollama가 실행되지 않았습니다!"
    echo "새 터미널에서 'ollama serve'를 실행하세요."
    echo ""
    read -p "계속하려면 Enter를 누르세요..."
fi

echo ""
echo "[3/3] Streamlit 앱 실행 중..."
echo "브라우저에서 자동으로 열립니다..."
echo ""

streamlit run app.py