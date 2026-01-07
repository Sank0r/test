import PyInstaller.__main__
import os
import shutil


project_dir = os.path.dirname(os.path.abspath(__file__))

def create_default_files():
    if not os.path.exists("users.db"):
        import sqlite3
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                login TEXT NOT NULL COLLATE BINARY,
                password TEXT NOT NULL COLLATE BINARY,
                description TEXT,
                birth_date TEXT,
                type NUMERIC NOT NULL DEFAULT 1,
                CONSTRAINT LOGIN PRIMARY KEY(login) ON CONFLICT ROLLBACK
            )
        ''')
        conn.commit()
        conn.close()
        print("Создан users.db")

    if not os.path.exists("settings.ini"):
        with open("settings.ini", "w", encoding="utf-8") as f:
            f.write("""[REGION_PARMS]
lang = ru
country = RU

[SCREEN_PREFERENCES]
resolution = 640x480

[SCREEN_PREFERENCES_MAIN]
resolution = 800x600
""")
        print("Создан settings.ini")

    if not os.path.exists("lang"):
        os.makedirs("lang")
        print("Создана папка lang")

    lang_files = {
        "en.json": '''{
    "noInternetAccess": "No internet access",
    "failedFetchPublicIP": "Failed to fetch public IP",
    "restarting": "Restarting...",
    "setNickname": "Nickname set to {0}",
    "notConnected": "Not connected to a peer",
    "failedConnectPeerUnkown": "Failed to connect: Peer IP or Port unknown",
    "alreadyConnected": "Already connected to a peer",
    "failedSaveLog": "Failed to save log",
    "savedLog": "Saved log to p2p-chat-log_{0}.log",
    "exitApp": "Exiting...",
    "commandNotFound": "Command not found",
    "commandWrongSyntax": "Wrong syntax for command {0}. Expected {1} arguments, got {2}",
    "commandList": "List of commands:",
    "serverStatusMessage": "Server: {0} | Port: {1} | Connection: {2}",
    "clientStatusMessage": "Client: {0} | Connected: {1}",
    "nicknameStatusMessage": "Nickname: {0}",
    "you": "YOU",
    "changingLang": "Changing language to {0}",
    "failedChangingLang": "Failed to change language",
    "commands": {
        "connect": "/connect [ip] [port] - Connect to a peer",
        "disconnect": "/disconnect - Disconnect from peer",
        "nickname": "/nickname [name] - Set your nickname",
        "quit": "/quit - Exit the application",
        "port": "/port [port] - Change server port",
        "connectback": "/connectback - Connect back to a peer that connected to you",
        "clear": "/clear - Clear the chat",
        "eval": "/eval [code] - Evaluate python code",
        "status": "/status - Show connection status",
        "log": "/log - Save chat log to file",
        "help": "/help - Show this help",
        "flowei": "/flowei - Open flowei.tech in browser",
        "lang": "/lang [language] - Change language"
    }
}''',
        "ru.json": '''{
    "noInternetAccess": "Нет доступа к интернету",
    "failedFetchPublicIP": "Не удалось получить публичный IP",
    "restarting": "Перезапуск...",
    "setNickname": "Никнейм установлен на {0}",
    "notConnected": "Не подключен к собеседнику",
    "failedConnectPeerUnkown": "Не удалось подключиться: IP или порт собеседника неизвестны",
    "alreadyConnected": "Уже подключен к собеседнику",
    "failedSaveLog": "Не удалось сохранить лог",
    "savedLog": "Лог сохранен в p2p-chat-log_{0}.log",
    "exitApp": "Выход...",
    "commandNotFound": "Команда не найдена",
    "commandWrongSyntax": "Неверный синтаксис для команды {0}. Ожидалось {1} аргументов, получено {2}",
    "commandList": "Список команд:",
    "serverStatusMessage": "Сервер: {0} | Порт: {1} | Подключение: {2}",
    "clientStatusMessage": "Клиент: {0} | Подключен: {1}",
    "nicknameStatusMessage": "Никнейм: {0}",
    "you": "ВЫ",
    "changingLang": "Смена языка на {0}",
    "failedChangingLang": "Не удалось сменить язык",
    "commands": {
        "connect": "/connect [ip] [port] - Подключиться к собеседнику",
        "disconnect": "/disconnect - Отключиться от собеседника",
        "nickname": "/nickname [имя] - Установить ваш никнейм",
        "quit": "/quit - Выйти из приложения",
        "port": "/port [порт] - Изменить порт сервера",
        "connectback": "/connectback - Подключиться обратно к собеседнику",
        "clear": "/clear - Очистить чат",
        "eval": "/eval [код] - Выполнить python код",
        "status": "/status - Показать статус подключения",
        "log": "/log - Сохранить лог чата в файл",
        "help": "/help - Показать эту справку",
        "flowei": "/flowei - Открыть flowei.tech в браузере",
        "lang": "/lang [язык] - Сменить язык"
    }
}'''
    }
    
    for filename, content in lang_files.items():
        filepath = os.path.join("lang", filename)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Создан {filename}")

print("Создание необходимых файлов...")
create_default_files()

# Параметры сборки PyInstaller
PyInstaller.__main__.run([
    'menu_reg.py',
    '--name=MyDrawingApp',
    '--noconsole',  
    '--onedir',
    # Основные модули
    '--hidden-import=db_main',
    '--hidden-import=common',
    '--hidden-import=grid_main',
    '--hidden-import=settings_qmenu',
    '--hidden-import=language_values',
    '--hidden-import=tray_icon',
    '--hidden-import=canvas',
    '--hidden-import=path_helper',
    '--hidden-import=sqlite3',
    # Файлы данных
    '--add-data=style.qss;.',
    '--add-data=icon.png;.',
    '--add-data=gear.png;.',
    '--add-data=icon1.png;.',
    '--add-data=icon2.png;.',
    '--add-data=icon3.png;.',
    '--add-data=icon4.png;.',
    '--add-data=icon5.png;.',
    '--add-data=icon6.png;.',
    '--add-data=8.png;.',
    '--add-data=9.png;.',
    '--add-data=settings.ini;.',     
    '--add-data=users.db;.',         
    # Папки
    '--add-data=lang;lang',
    '--icon=icon.png',
    '--clean',
])

print("\nСборка завершена!")
print("EXE файл находится в папке dist/MyDrawingApp/")
