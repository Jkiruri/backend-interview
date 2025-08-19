# PowerShell script to start Celery workers for OrderFlow

Write-Host "Starting Celery Workers for OrderFlow..." -ForegroundColor Green
Write-Host ""

# Function to start a Celery worker
function Start-CeleryWorker {
    param(
        [string]$Queue,
        [string]$Title,
        [int]$Concurrency = 2
    )
    
    Write-Host "Starting $Title..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "celery -A orderflow worker -Q $Queue -l info --concurrency=$Concurrency" -WindowStyle Normal
    Start-Sleep -Seconds 2
}

# Start different workers
Start-CeleryWorker -Queue "sms" -Title "SMS Worker" -Concurrency 2
Start-CeleryWorker -Queue "email" -Title "Email Worker" -Concurrency 3
Start-CeleryWorker -Queue "notifications" -Title "General Notifications Worker" -Concurrency 2

# Start Celery Beat
Write-Host "Starting Celery Beat (Scheduler)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "celery -A orderflow beat -l info" -WindowStyle Normal
Start-Sleep -Seconds 2

# Start Flower
Write-Host "Starting Flower (Monitoring)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "celery -A orderflow flower --port=5555" -WindowStyle Normal

Write-Host ""
Write-Host "All Celery services started!" -ForegroundColor Green
Write-Host ""
Write-Host "Monitoring URLs:" -ForegroundColor Cyan
Write-Host "- Flower: http://localhost:5555" -ForegroundColor White
Write-Host "- RabbitMQ Management: http://localhost:15672 (guest/guest)" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
