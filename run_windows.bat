@echo off
REM Windows batch file to run the financial tracker

echo ========================================
echo Financial Tracker - Windows Launcher
echo ========================================
echo.

:menu
echo What would you like to do?
echo.
echo 1. Test price fetcher (verify it works)
echo 2. Initialize database with sample data
echo 3. Setup complete database
echo 4. Update all prices
echo 5. Run the application
echo 6. Exit
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto test
if "%choice%"=="2" goto init
if "%choice%"=="3" goto setup
if "%choice%"=="4" goto update
if "%choice%"=="5" goto run
if "%choice%"=="6" goto end

echo Invalid choice, please try again.
goto menu

:test
echo.
echo Testing price fetcher...
python test_price_fetcher.py
echo.
pause
goto menu

:init
echo.
echo Initializing database with sample data...
python init_db.py sample
echo.
pause
goto menu

:setup
echo.
echo Setting up complete database...
python setup_complete_db.py
echo.
pause
goto menu

:update
echo.
echo Updating all asset prices...
python -c "from batch_price_fetcher import update_all_prices_batch; update_all_prices_batch()"
echo.
pause
goto menu

:run
echo.
echo Starting Flask application...
echo Visit: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py
goto menu

:end
echo.
echo Goodbye!
