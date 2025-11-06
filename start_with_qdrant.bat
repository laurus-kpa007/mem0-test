@echo off
echo ========================================
echo mem0 LTM 시스템 (Qdrant 포함) 시작
echo ========================================
echo.

echo [1/5] 가상환경 활성화 중...
call venv\Scripts\activate.bat

echo.
echo [2/5] Qdrant 실행 상태 확인 중...
curl -s http://localhost:6333 >nul 2>&1
if %errorlevel% equ 0 (
    echo Qdrant가 이미 실행 중입니다!
) else (
    echo Qdrant가 실행되지 않았습니다.
    echo.
    echo 옵션 선택:
    echo 1. Docker로 Qdrant 실행
    echo 2. 바이너리로 Qdrant 실행
    echo 3. Qdrant 없이 계속 (ChromaDB 사용)
    echo.
    set /p choice="선택 (1-3): "

    if "!choice!"=="1" (
        echo Docker로 Qdrant 시작 중...
        docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v "%cd%\qdrant_storage:/qdrant/storage:z" qdrant/qdrant
        timeout /t 5 >nul
    ) else if "!choice!"=="2" (
        echo 새 창에서 Qdrant 바이너리를 실행하세요...
        start cmd /k "cd /d %cd% && qdrant\qdrant.exe"
        timeout /t 5 >nul
    )
)

echo.
echo [3/5] Ollama 서비스 확인 중...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama가 실행되지 않았습니다!
    echo 새 창에서 'ollama serve'를 실행하세요.
    echo.
    pause
)

echo.
echo [4/5] 서비스 상태 확인...
python -c "import requests; r=requests.get('http://localhost:6333', timeout=2); print('Qdrant: OK')" 2>nul || echo Qdrant: ChromaDB로 대체됨
python -c "import ollama; print('Ollama: OK')" 2>nul || echo Ollama: 확인 필요

echo.
echo [5/5] Streamlit 앱 실행 중...
echo 브라우저에서 자동으로 열립니다...
echo.

streamlit run app.py

pause