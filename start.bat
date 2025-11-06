@echo off
echo ========================================
echo mem0 LTM 시스템 시작
echo ========================================
echo.

echo [1/3] 가상환경 활성화 중...
call venv\Scripts\activate.bat

echo.
echo [2/3] Ollama 서비스 확인 중...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama가 실행되지 않았습니다!
    echo 새 창에서 'ollama serve'를 실행하세요.
    echo.
    pause
)

echo.
echo [3/3] Streamlit 앱 실행 중...
echo 브라우저에서 자동으로 열립니다...
echo.

streamlit run app.py

pause