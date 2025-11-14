@echo off
REM Start Django server on all network interfaces
REM This allows access from other computers on the network
REM Access URL: http://YOUR_COMPUTER_IP:8000

echo Starting Django server on 0.0.0.0:8000
echo.
echo To find your IP address, run: ipconfig
echo Then access from another computer: http://YOUR_IP:8000
echo.

python manage.py runserver 0.0.0.0:8000

pause
