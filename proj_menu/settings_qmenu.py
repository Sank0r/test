import configparser

class SettingsManager:
    __config = None
    __sections = None
    
    @staticmethod
    def read_settings():
        SettingsManager.__config = configparser.ConfigParser()
        SettingsManager.__config.read("settings.ini")
        SettingsManager.__sections = SettingsManager.__config.sections()

    @staticmethod
    def get_next_section():
        current_section = 0
        def read_section():
            nonlocal current_section
            if current_section < len(SettingsManager.__sections):
                sect = SettingsManager.__sections[current_section]
                key_value = {}
                for key in SettingsManager.__config[sect]:
                    value = SettingsManager.__config.get(sect, key)
                    key_value[key] = value
                current_section += 1
                return (key_value, sect)
            return dict()
        return read_section

    @staticmethod
    def save_settings():
        with open("settings.ini", "w") as configfile:
            SettingsManager.__config.write(configfile)
    
    @staticmethod
    def set_setting(sn,pn,pv):
        print(sn,pn,pv)
        SettingsManager.__config[sn][pn] = pv

    @staticmethod
    def default_setting(section,key):
        value = SettingsManager.__config.get(section,key)
        return value
        
    
