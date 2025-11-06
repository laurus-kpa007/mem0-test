@echo off
echo ========================================
echo mem0 LTM 최소 패키지 설치
echo ========================================
echo.
echo Python 버전 호환성 문제를 피하기 위한 최소 설치입니다.
echo.

echo [1/3] pip 업그레이드...
python -m pip install --upgrade pip

echo.
echo [2/3] 최소 필수 패키지 설치...
pip install -r requirements-minimal.txt

echo.
echo [3/3] Ollama 모델 확인...
ollama list

echo.
echo ========================================
echo 설치 완료!
echo.
echo 다음 단계:
echo 1. ollama serve (새 창에서)
echo 2. streamlit run app.py
echo ========================================
pause