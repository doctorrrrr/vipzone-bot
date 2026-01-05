# VIPZone Bot

Простий Telegram-бот для пінгу та трасировки мережевих пристроїв. Це був проект для швидкого моніторінгу та автоматизації деяких процесів з допомогою функціоналу телеграм ботів. Там ще є погода, маленький нотатник та будильник з нагадуванннями.... Наче працює)

📁 Структура
/opt/vipzone/bots/bot/ 
├── bot.py # Основна логіка бота 
├── bot.sh # Скрипт запуску 
├── config.py # Конфігурація 
├── requirements.txt 
# Python-залежності 
└── .env # (опціонально) конфіг для змінних середовища

🚀 Запуск
# VIPZone Telegram Bot

Простий Telegram-бот, розміщений на локальному сервері. Працює без контейнерів, з мінімумом ресурсів. Обробка заявок / системна автоматизація.

## 📂 Структура

/opt/vipzone/bots/bot/ ├── bot.py # Основний код бота ├── bot.sh # Стартовий скрипт ├── config.py # Конфігураційний файл (виключений з гіта) ├── requirements.txt # Залежності └── .git/ # Репозиторій


## 🧾 Запуск

```bash
./bot.sh

або через systemd:

systemctl start bot.service
systemctl enable bot.service

/etc/systemd/system/bot.service:

[Unit]
Description=Bot
After=default.target

[Service]
ExecStart=/opt/vipzone/bots/bot/bot.sh
Restart=always
User=root

[Install]
WantedBy=default.target

⚙️ Конфігурація

Налаштування зберігаються в config.py, який не додається в гіт. Містить токени, ID, логіку маршрутизації повідомлень тощо.

    Для прикладу: config.example.py

🧰 Автодеплой (планується)

📥 Встановлення залежностей

pip3 install -r requirements.txt

🚀 Автодеплой (у процесі)

📦 Бекапи (плануються)
    GitHub Actions через SSH → git pull + systemctl restart

    Альтернатива: локальний puller.sh по webhook

🔐 Безпека

    Жодних паролів чи токенів у репозиторії.

    Конфіг config.py локальний, додається в .gitignore.

💾 Бекап (планується)

    dump + rsync/архів

    лог у /var/log/backups.log

👨‍🔧 Проєкт є частиною персональної інфраструктури на vipzone.net.ua
