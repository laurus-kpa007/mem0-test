@echo off
echo ========================================
echo mem0 LTM 테스트 스위트
echo ========================================
echo.

echo [1/4] 시스템 기본 테스트...
echo ----------------------------------------
python test_system.py
echo.

echo [2/4] mem0 핵심 기능 테스트...
echo ----------------------------------------
python test_mem0_core_features.py
echo.

echo [3/4] 강화된 채팅 서비스 테스트...
echo ----------------------------------------
python test_enhanced_chat.py
echo.

echo [4/4] 웹 UI 실행...
echo ----------------------------------------
echo.
echo 웹 UI를 실행하시겠습니까? (Y/N)
set /p answer=선택:

if /i "%answer%"=="Y" (
    echo.
    echo 웹 UI를 실행합니다...
    echo 브라우저에서 http://localhost:8501 접속
    echo 종료하려면 Ctrl+C
    echo.
    streamlit run app.py
) else (
    echo.
    echo 테스트 완료!
)

pause