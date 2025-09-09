class LanguageConstants:
    _ENG = 0
    _RU = 1
    
    # Общие сообщения
    STYLESHEET_FILE_NOT_FOUND = ["file styles not found!", "Файл стилей не найден!"]
    MINIMIZE_TO_TRAY = ["Minimize to Tray", "Свернуть в трей"]
    INVALID_CREDENTIALS = ["Invalid username or password", "Неверный логин или пароль"]
    APP_EXITING = ["Application exiting...", "Завершение приложения..."]
    
    # Заголовки окон
    MAIN_WINDOW = ["Main Window", "Главное окно"]
    LOGIN_WINDOW = ["Login", "Вход"]
    REGISTER_WINDOW = ["Registration", "Регистрация"]
    SETTINGS_WINDOW = ["Settings", "Настройки"]
    GRID_WINDOW = ["Tools", "Инструменты"]
    
    # Заголовки и кнопки
    SETTINGS = ["Settings", "Настройки"]
    SAVE = ["Save", "Сохранить"]
    SETTINGS_SAVED = ["Settings saved successfully!", "Настройки успешно сохранены!"]
    LOGIN = ["Login", "Войти"]
    REGISTER = ["Register", "Зарегистрироваться"]
    BACK = ["Back", "Назад"]
    CONNECTION = ["Connection", "Подключение"]
    SHOW = ["Show", "Показать"]
    EXIT = ["Exit", "Выход"]
    MANAGER = ["Manager", "Управление"]
    NETWORK = ["Network", "Сеть"]
    CHOOSE_COLOR = ["Choose color", "Выберите цвет"]
    LANGUAGE = ["Language", "Язык"]
    
    # Поля формы
    USERNAME_WINDOW = ["Username:", "Логин:"]
    USERNAME = ["Username", "Логин"]
    NICKNAME = ["Nickname:", "Никнейм:"]
    DATE_OF_BIRTH = ["Date of birth:", "Дата рождения:"]
    PASSWORD_WINDOW = ["Password:", "Пароль:"]
    DESCRIPTION = ["Description", "Описание"]
    
    # Подсказки в полях ввода
    USERNAME_PLACEHOLDER = ["Enter username", "Введите логин"]
    PASSWORD_PLACEHOLDER = ["Enter password", "Введите пароль"]
    NICKNAME_PLACEHOLDER = ["Enter your nickname", "Введите ваш никнейм"]
    
    # Сообщения о регистрации
    REGISTRATION_COMPLETED_QMENU = ["Successfully", "Успешно"]
    REGISTRATION_COMPLETED = ["Registration was successful", "Регистрация прошла успешно"]
    
    # Сообщения об ошибках
    WARNING = ["Warning", "Предупреждение"]
    ERROR = ["Error", "Ошибка"]
    CRITICAL = ["Critical", "Критическая ошибка"]
    USER_ERROR = ["User Error", "Ошибка пользователя"]
    DATABASE_ERROR = ["Database Error", "Ошибка базы данных"]
    USER_ALREADY_EXISTS = ["The user with this username already exists", "Пользователь с таким логином уже существует"]
    USERNAME_EMPTY = ["Username cannot be empty", "Логин не может быть пустым"]
    PASSWORD_EMPTY = ["Password cannot be empty", "Пароль не может быть пустым"]
    PASSWORD_TOO_SHORT = ["Password must be at least 6 characters long", "Пароль должен содержать минимум 6 символов"]
    USERNAME_TOO_SHORT = ["Username must be at least 6 characters long", "Логин должен содержать минимум 6 символов"]
    FILE_NOT_FOUND = ["File not found", "Файл не найден"]
    FAILED_TO_LOAD_IMAGE = ["Failed to load image", "Не удалось загрузить изображение"]
    FAILED_TO_SAVE_IMAGE = ["Failed to save image", "Не удалось сохранить изображение"]
    LOAD_ERROR = ["Loading error", "Ошибка загрузки"]
    
    # Названия инструментов
    PENCIL = ["Pencil", "Карандаш"]
    COLOR_PICKER = ["Color Picker", "Выбор цвета"]
    ERASER = ["Eraser", "Ластик"]
    TEXT = ["Text", "Текст"]
    SHAPES = ["Shapes", "Фигуры"]
    ZOOM = ["Zoom", "Масштаб"]
    SAVE_IMAGE = ["Save", "Сохранить"]
    LOAD_IMAGE = ["Load", "Загрузить"]
    
    # Названия фигур
    RECTANGLE = ["Rectangle", "Прямоугольник"]
    CIRCLE = ["Circle", "Круг"]
    LINE = ["Line", "Линия"]
    
    # Настройки масштаба и размеров
    ZOOM_LEVEL = ["Zoom: {}%", "Масштаб: {}%"]
    LINE_WIDTH = ["Line width: {}", "Толщина линии: {}"]
    ERASER_SIZE = ["Eraser size: {}", "Размер ластика: {}"]
    TEXT_SIZE = ["Text size: {}", "Размер текста: {}"]
    
    # Названия секций и параметров
    SECTION_NAMES = {
        "REGION_PARMS": ["Region", "Регион"],
        "SCREEN_PREFERENCES": ["Login Screen", "Экран входа"],
        "SCREEN_PREFERENCES_MAIN": ["Main Screen", "Главный экран"]
    }
    
    PARAM_NAMES = {
        "lang": ["Language", "Язык"],
        "country": ["Country", "Страна"],
        "resolution": ["Resolution", "Разрешение"]
    }

    @staticmethod
    def get_constant(name, language):
        try:
            index = LanguageConstants._RU if language.lower() == "ru" else LanguageConstants._ENG
            return getattr(LanguageConstants, name)[index]
        except (AttributeError, IndexError):
            return name
            
    @staticmethod
    def get_section_name(section_key, language):
        try:
            index = LanguageConstants._RU if language.lower() == "ru" else LanguageConstants._ENG
            return LanguageConstants.SECTION_NAMES.get(section_key, [section_key, section_key])[index]
        except (AttributeError, IndexError):
            return section_key
            
    @staticmethod
    def get_param_name(param_key, language):
        try:
            index = LanguageConstants._RU if language.lower() == "ru" else LanguageConstants._ENG
            return LanguageConstants.PARAM_NAMES.get(param_key, [param_key, param_key])[index]
        except (AttributeError, IndexError):
            return param_key
            
    @staticmethod
    def format_translation(key, language, *args):
        template = LanguageConstants.get_constant(key, language)
        return template.format(*args)
