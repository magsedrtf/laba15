# Бесконечный цикл системного мониторинга
while ($true) {
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] Фоновый мониторинг активности PowerShell в Сессии 0. Статус: OK"
    
    # Запись в системный лог-файл
    Add-Content -Path "C:\ps_service_log.txt" -Value $LogMessage
    
    # Низкоуровневая пауза потока на 5 секунд
    Start-Sleep -Seconds 5
}
