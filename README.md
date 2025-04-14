# VIPZone Bot

Простий Telegram-бот для пінгу та трасировки мережевих пристроїв. Це був проект для вивчення пайтона та функціоналу телеграм ботів. Там ще є погода, маленький нотатник та будильник з нагадуванннями.... Наче працює)

## 📁 Структура
/opt/vipzone/bots/bot/ 
├── bot.py # Основна логіка бота 
├── bot.sh # Скрипт запуску 
├── config.py # Конфігурація 
├── requirements.txt 
# Python-залежності 
└── .env # (опціонально) конфіг для змінних середовища

## 🚀 Запуск

```bash
./bot.sh
або через systemd:
systemctl start bot.service
systemctl enable bot.service

## ⚙️ Налаштування

Всі налаштування в config.py. Там вказані токени, ID, параметри тощо.

    УВАГА: config.py не комітиться в репозиторій! Замість нього — config.py.example.

## 🐍 Встановлення залежностей

pip install -r requirements.txt

## 🧠 Автозапуск

У systemd:

[Unit]
Description=Bot
After=network.target

[Service]
ExecStart=/opt/vipzone/bots/bot/bot.sh
Restart=always
User=root

[Install]
WantedBy=multi-user.target

## 🧰 Автодеплой (планується)

    через GitHub Actions → SSH → git pull + systemctl restart

    або через webhook + puller.sh

## 📦 Бекапи (плануються)

    Архів коду + дамп БД (якщо треба)

    Логи у /var/log/backups.log



💡 Цей бот є частиною інфраструктури vipzone.net.ua


Хочеш, я його одразу підлаштую під твій конкретний бот і структуру, якщо кинеш мені `config.py` або скажеш, що там у тебе за функціонал?

