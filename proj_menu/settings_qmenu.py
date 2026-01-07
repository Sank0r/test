import configparser
import os
from path_helper import get_writable_path

class SettingsManager:
    __config = None
    __sections = None
    
    @staticmethod
    def read_settings():
        SettingsManager.__config = configparser.ConfigParser()
        path = get_writable_path("settings.ini")
        
        if not os.path.exists(path):
            SettingsManager.__config['REGION_PARMS'] = {
                'lang': 'ru',
                'country': 'RU'
            }
            SettingsManager.__config['SCREEN_PREFERENCES'] = {
                'resolution': '640x480'
            }
            SettingsManager.__config['SCREEN_PREFERENCES_MAIN'] = {
                'resolution': '800x600'
            }
            SettingsManager.save_settings()
            print(f"DEBUG: Создан settings.ini по умолчанию: {path}")
        
        SettingsManager.__config.read(path, encoding='utf-8')
        SettingsManager.__sections = SettingsManager.__config.sections()

    @staticmethod
    def save_settings():
        path = get_writable_path("settings.ini")
        with open(path, "w", encoding='utf-8') as configfile:
            SettingsManager.__config.write(configfile)
        print(f"DEBUG: Настройки сохранены в: {path}")
    
    @staticmethod
    def get_next_section():
        current_section = 0
        def read_section():
            nonlocal current_section
            if SettingsManager.__sections and current_section < len(SettingsManager.__sections):
                sect = SettingsManager.__sections[current_section]
                key_value = {key: SettingsManager.__config.get(sect, key) for key in SettingsManager.__config[sect]}
                current_section += 1
                return (key_value, sect)
            return dict()
        return read_section

    @staticmethod
    def set_setting(sn,pn,pv):
        if not SettingsManager.__config.has_section(sn):
            SettingsManager.__config.add_section(sn)
        SettingsManager.__config[sn][pn] = pv

    @staticmethod
    def default_setting(section, key):
        try:
            return SettingsManager.__config.get(section, key)
        except:
            defaults = {
                "lang": "ru",
                "country": "RU",
                "resolution": "640x480"
            }
            return defaults.get(key, "")
