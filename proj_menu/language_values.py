class LanguageConstants:
    _ENG = 0
    _RU = 1
    
    # Общие сообщения
    STYLESHEET_FILE_NOT_FOUND = ["file styles not found!", "Файл стилей не найден!"]
    MINIMIZE_TO_TRAY = ["Minimize to Tray", "Свернуть в трей"]
    
    # Заголовки и кнопки
    SETTINGS = ["Settings", "Настройки"]
    SAVE = ["Save", "Сохранить"]
    SETTINGS_SAVED = ["Settings saved successfully!", "Настройки успешно сохранены!"]
    LOGIN = ["Login", "Вход"]
    REGISTER = ["Registration", "Регистрация"]
    BACK = ["Back", "Назад"]
    
    # Поля формы
    USERNAME_WINDOW = ["Username:", "Логин:"]
    USERNAME = ["Username", "Логин"]
    NICKNAME = ["Nickname:", "Никнейм:"]
    DATE_OF_BIRTH = ["Date of birth:", "Дата рождения:"]
    PASSWORD_WINDOW = ["Password:", "Пароль:"]
    
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
    USER_ERROR = ["User Error", "Ошибка пользователя"]
    DATABASE_ERROR = ["Database Error", "Ошибка базы данных"]
    USER_ALREADY_EXISTS = ["The user with this username already exists", "Пользователь с таким логином уже существует"]
    USERNAME_EMPTY = ["Username cannot be empty", "Логин не может быть пустым"]
    PASSWORD_EMPTY = ["Password cannot be empty", "Пароль не может быть пустым"]
    PASSWORD_TOO_SHORT = ["Password must be at least 6 characters long", "Пароль должен содержать минимум 6 символов"]
    USERNAME_TOO_SHORT = ["Username must be at least 6 characters long", "Логин должен содержать минимум 6 символов"]
    
    @staticmethod
    def get_constant(name, language):
        try:
            index = LanguageConstants._RU if language.lower() == "ru" else LanguageConstants._ENG
            return getattr(LanguageConstants, name)[index]
        except (AttributeError, IndexError):
            return name