# Контрольные вопросы — краткие ответы

## 1. Почему `sc create` для `python.exe script.py` даёт Error 1053? Чего ждёт SCM?

- `sc create` только пишет запись в реестр (`HKLM\SYSTEM\CurrentControlSet\Services`) — ошибка возникает на `sc start`.
- При старте службы SCM (`services.exe`) в течение 30 с (параметр `ServicesPipeTimeout`) ждёт от процесса:
  1. вызова `StartServiceCtrlDispatcher()` — подключения главного потока к именованному каналу `\\.\pipe\ntsvcs` и регистрации `ServiceMain`;
  2. отчётов `SetServiceStatus()`: `START_PENDING` → `RUNNING`;
  3. реакции на управляющие коды STOP / PAUSE / SHUTDOWN.
- `python.exe` / `powershell.exe` — обычные консольные приложения Ring 3: про протокол SCM не знают, канал не открывают, зацикленный скрипт «молчит» → через 30 с SCM убивает процесс → **Error 1053**.
- Вывод: нужна обертка, реализующая протокол службы (`win32serviceutil.ServiceFramework`), а скрипт исполняется уже внутри её потока.

## 2. Почему `sc query` не видит PowerShell-задание (ошибка 1060)?

- `sc.exe` работает **только с базой SCM**: реестр `HKLM\SYSTEM\CurrentControlSet\Services` + `services.exe`. `OpenService()` не находит имя задания → `1060 ERROR_SERVICE_DOES_NOT_EXIST`.
- Scheduled Job — элемент **другой подсистемы**: служба «Планировщик заданий» (Schedule, `svchost.exe`, Task Scheduler 2.0) + модуль **PSScheduledJob** (`Get-ScheduledJob`, `Start-ScheduledJob`).
- Хранение: XML-манифест `JobDefinition.xml` в `...\Microsoft.PowerShell.Core\ScheduledJob\<имя>`; в `taskschd.msc` — контейнер `\Microsoft\Windows\PowerShell\ScheduledJobs`.
- Проверка: `Get-ScheduledJob`, `schtasks /query /tn "\Microsoft\Windows\PowerShell\ScheduledJobs\PowerShellBackgroundMonitor"`.
- Сходство со службой (фон, Сессия 0) внешнее: у Планировщика свой API и своя база, прямой связи со SCM нет.
- Практика: процесс задания работает в Сессии 0 от учётной записи регистратора (S4U-вход), а не от SYSTEM; службы SCM по умолчанию — LocalSystem.

## 3. Что такое Execution Policy, зачем RemoteSigned, какие риски?

- Механизм PowerShell, задающий условия запуска `.ps1`-скриптов. Уровни: `Restricted` (по умолчанию — скрипты запрещены), `AllSigned`, `RemoteSigned`, `Unrestricted`, `Bypass`. Области (по приоритету): MachinePolicy/UserPolicy (GPO) → Process → CurrentUser → LocalMachine (реестр).
- `RemoteSigned`: локальные скрипты — без подписи; скачанные из сети (метка MOTW, поток `Zone.Identifier`) — только подписанные доверенным издателем.
- Зачем менять: при `Restricted` фоновый PowerShell не выполнит `win_monitor.ps1` — задание стартует и молча завершается, лог пустой. `RemoteSigned` — минимально достаточный уровень.
- Риски (Ring 3): содержимое локальных скриптов не проверяется — вектор закрепления ВПО с привилегиями запустившей учётки; политика **не является security boundary** — обходится `-ExecutionPolicy Bypass` / `-Command` / чтением скрипта в память.
- Компенсации: NTFS-права на папку скриптов (запись — только админам), Code Signing, AppLocker/WDAC, Script Block Logging.
