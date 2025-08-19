@echo off
echo Starting Celery Workers for OrderFlow...
echo.

echo Starting SMS Worker...
start "Celery SMS Worker" cmd /k "celery -A orderflow worker -Q sms -l info --concurrency=2"

echo Starting Email Worker...
start "Celery Email Worker" cmd /k "celery -A orderflow worker -Q email -l info --concurrency=3"

echo Starting General Notifications Worker...
start "Celery Notifications Worker" cmd /k "celery -A orderflow worker -Q notifications -l info --concurrency=2"

echo Starting Celery Beat (Scheduler)...
start "Celery Beat" cmd /k "celery -A orderflow beat -l info"

echo Starting Flower (Monitoring)...
start "Flower" cmd /k "celery -A orderflow flower --port=5555"

echo.
echo All Celery services started!
echo.
echo Monitoring URLs:
echo - Flower: http://localhost:5555
echo - RabbitMQ Management: http://localhost:15672 (guest/guest)
echo.
pause
