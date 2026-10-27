import win32serviceutil
import win32service
import win32event
import time
import os

class PyBackgroundService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PyBackgroundService"
    _svc_display_name_ = "System Programming - Python Script Service Wrapper"
    _svc_description_ = "Обертка для запуска скриптов Python внутри диспетчера SCM Windows."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        log_file = "C:\\py_service_log.txt"
        
        while self.is_running:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] Python-скрипт успешно выполняется под управлением SCM. PID: {os.getpid()}\n")
            
            rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
            if rc == win32event.WAIT_OBJECT_0:
                break

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PyBackgroundService)
