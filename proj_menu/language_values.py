class LanguageConstants:
    _ENG = 0
    _RU = 1
    STYLESHEET_FILE_NOT_FOUND = ["file styles not found!", "Файл стилей не найден!"]

    MINIMIZE_TO_TRAY = ["Свернуть в трей","Minimize to Tray"]
    RESTORE_FROM_TRAY = ["Убрать из трея", "Restore from Tray"]

    SETTINGS = ["Settings", "Настройки"]
    SAVE = ["Save", "Сохранить"]
    SETTINGS_SAVED = ["Settings saved successfully!", "Настройки успешно сохранены!"]
    LOGIN = ["Login", "Вход"]
    REGISTER = ["Registation", "Регистрация"]
    BACK = ["Back", "Назад"]
    
    USERNAME_WINDOW = ["Login:", "Вход:"]
    USERNAME = ["Username", "Логин"]
    NICKNAME = ["Nickname:", "Никнейм:"]
    DATE_OF_BIRTH = ["Date of birth:", "Дата рождения:"]
    PASSWORD_WINDOW = ["Password:", "Пароль:"]
    
    USERNAME_PLACEHOLDER = ["Enter username", "Введите логин"]
    PASSWORD_PLACEHOLDER = ["Enter password", "Введите пароль"]
    NICKNAME_PLACEHOLDER = ["Enter your nickname", "Напишите ваш nickname"]

    REGISTRATION_COMLETED_QMENU = ["Successfully", "Успешно"]
    REGISTRATION_COMLETED = ["Registration was successful","Регистрация прошла успешно"]
    USER_ERROR = ["Error", "Ошибка"]
    USER_ALREADY_EXISTS =["The user with this username already exists", "Пользователь с таким логином уже существует" ]

    
    @staticmethod
    def get_constant(name, language):
        try:
            index = LanguageConstants._RU if language.lower() == "ru" else LanguageConstants._ENG
            return getattr(LanguageConstants, name)[index]
        except (AttributeError, IndexError):
            return name


