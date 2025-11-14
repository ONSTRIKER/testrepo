@echo off
REM Fix .env file to use SQLite instead of PostgreSQL
REM ==================================================

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo.
echo ============================================
echo Fixing .env file for SQLite
echo ============================================
echo.

REM Backup existing .env
if exist .env (
    copy .env .env.backup >nul 2>&1
    echo Created backup: .env.backup
)

REM Create new .env with SQLite configuration
(
echo # Master Creator v3 MVP - Environment Configuration
echo # ═══════════════════════════════════════════════════════════
echo.
echo # API Keys
echo # ═══════════════════════════════════════════════════════════
echo # IMPORTANT: Replace with your actual Anthropic API key
echo ANTHROPIC_API_KEY=%ANTHROPIC_API_KEY%
echo.
echo # ═══════════════════════════════════════════════════════════
echo # Database Configuration (SQLite for local development^)
echo # ═══════════════════════════════════════════════════════════
echo DATABASE_URL=sqlite:///./master_creator.db
echo.
echo # ═══════════════════════════════════════════════════════════
echo # Vector Store Configuration (Local Chroma^)
echo # ═══════════════════════════════════════════════════════════
echo CHROMA_PERSIST_DIRECTORY=./chroma_data
echo.
echo # ═══════════════════════════════════════════════════════════
echo # Application Settings
echo # ═══════════════════════════════════════════════════════════
echo APP_ENV=development
echo API_HOST=0.0.0.0
echo API_PORT=8080
echo LOG_LEVEL=INFO
echo.
echo # ═══════════════════════════════════════════════════════════
echo # LLM Configuration
echo # ═══════════════════════════════════════════════════════════
echo LLM_MODEL=claude-sonnet-4-5-20250929
echo LLM_MAX_TOKENS=4096
echo LLM_TEMPERATURE=0.7
echo ENABLE_PROMPT_CACHING=true
echo.
echo # ═══════════════════════════════════════════════════════════
echo # Cost Management
echo # ═══════════════════════════════════════════════════════════
echo MAX_COST_PER_REQUEST=1.00
echo DAILY_BUDGET_LIMIT=50.00
echo ENABLE_RATE_LIMITING=true
echo.
echo # ═══════════════════════════════════════════════════════════
echo # Educational Compliance
echo # ═══════════════════════════════════════════════════════════
echo ENABLE_FERPA_LOGGING=true
echo ENABLE_AUDIT_TRAIL=true
echo.
echo # ═══════════════════════════════════════════════════════════
echo # Performance Settings
echo # ═══════════════════════════════════════════════════════════
echo MAX_CONCURRENT_STUDENTS=2250
echo.
echo # ═══════════════════════════════════════════════════════════
echo # Testing ^& Development
echo # ═══════════════════════════════════════════════════════════
echo ENABLE_SYNTHETIC_DATA=true
echo NUM_SYNTHETIC_STUDENTS=18
) > .env.temp

REM Read the API key from old .env if it exists
if exist .env.backup (
    for /f "tokens=2 delims==" %%a in ('findstr /C:"ANTHROPIC_API_KEY=" .env.backup') do set OLD_KEY=%%a
    if defined OLD_KEY (
        powershell -Command "(gc .env.temp) -replace 'ANTHROPIC_API_KEY=.*', 'ANTHROPIC_API_KEY=%OLD_KEY%' | Out-File -encoding ASCII .env"
        del .env.temp
        echo.
        echo ============================================
        echo SUCCESS: .env file updated!
        echo ============================================
        echo.
        echo - Database changed to SQLite
        echo - Your API key has been preserved
        echo - Old file backed up to .env.backup
        echo.
    ) else (
        move .env.temp .env >nul
        echo.
        echo ============================================
        echo WARNING: Could not find API key
        echo ============================================
        echo.
        echo Please edit .env and add your Anthropic API key
        echo.
    )
) else (
    move .env.temp .env >nul
    echo.
    echo ============================================
    echo .env file created
    echo ============================================
    echo.
    echo Please edit .env and add your Anthropic API key
    echo.
)

echo You can now run: start_server.bat
echo.
pause
