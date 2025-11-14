# Start Django server on all network interfaces
# This allows access from other computers on the network
# Access URL: http://YOUR_COMPUTER_IP:8000

Write-Host "Starting Django server on 0.0.0.0:8000" -ForegroundColor Green
Write-Host ""
Write-Host "To find your IP address, run: ipconfig" -ForegroundColor Cyan
Write-Host "Then access from another computer: http://YOUR_IP:8000" -ForegroundColor Cyan
Write-Host ""

python manage.py runserver 0.0.0.0:8000
