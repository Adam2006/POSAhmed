@echo off
echo ============================================================
echo POS Mock Data Generator
echo ============================================================
echo.
echo Select an option:
echo 1. Generate 50 orders (last 30 days) - Quick test
echo 2. Generate 100 orders (last 60 days) - Medium test
echo 3. Generate 200 orders (last 90 days) - Large test
echo 4. Custom (you enter the numbers)
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Generating 50 orders over last 30 days...
    python generate_mock_data.py 50 30
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Generating 100 orders over last 60 days...
    python generate_mock_data.py 100 60
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Generating 200 orders over last 90 days...
    python generate_mock_data.py 200 90
    goto end
)

if "%choice%"=="4" (
    echo.
    set /p num_orders="Enter number of orders: "
    set /p days_back="Enter number of days back: "
    echo.
    echo Generating %num_orders% orders over last %days_back% days...
    python generate_mock_data.py %num_orders% %days_back%
    goto end
)

if "%choice%"=="5" (
    echo Exiting...
    exit /b
)

echo Invalid choice!

:end
echo.
echo ============================================================
pause
