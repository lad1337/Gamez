from plugins import System
from gamez import common


# this class is special because it will be set to SYSTEM in the whole app
class SystemConfig(System):
    version = "0.15"
    _config = {'login_user': '',
               'login_password': '',
               'port': 8085,
               'socket_host': '0.0.0.0',
               'https': False,
               'interval_search': 120, # minutes
               'interval_update': 1440, # minutes
               'interval_check': 3,
               'blacklist_wii': '',
               'blacklist_ps3': '',
               'blacklist_xbox360': '',
               'blacklist_pc': '',
               'enabled': True,
               'check_path_wii': '',
               'check_path_ps3': '',
               'check_path_xbox360': '',
               'check_path_pc': '',
               'again_on_fail': False
               }
    config_meta = {'login_user': {'on_change_actions': ['reboot']},
                    'login_password': {'on_change_actions': ['reboot']},
                    'blacklist_wii': {'human': 'Blacklist for Wii', 'helper': 'list', 'placeholder': 'separated by ,'},
                    'blacklist_ps3': {'human': 'Blacklist for PS3', 'helper': 'list', 'placeholder': 'separated by ,'},
                    'blacklist_xbox360': {'human': 'Blacklist for Xbox360', 'helper': 'list', 'placeholder': 'separated by ,'},
                    'blacklist_pc': {'human': 'Blacklist for PC', 'helper': 'list', 'placeholder': 'separated by ,'},
                    'interval_search': {'human': 'Search interval (minutes)'},
                    'interval_update': {'human': 'Update interval (minutes)'},
                    'https': {'human': 'HTTPS'},
                    'check_path_wii': {'human': 'Check for Wii games in', 'placeholder': 'Absolute Path'},
                    'check_path_ps3': {'human': 'Check for PS3 games in', 'placeholder': 'Absolute Path'},
                    'check_path_xbox360': {'human': 'Check for Xbox360 games in', 'placeholder': 'Absolute Path'},
                    'check_path_pc': {'human': 'Check for PC games in', 'placeholder': 'Absolute Path'},
                    'interval_search': {'human': 'Search for games interval (minutes)', 'on_change_actions': ['reboot']},
                    'interval_update': {'human': 'Update games interval (minutes)', 'on_change_actions': ['reboot']},
                    'interval_check': {'human': 'Download check interval (minutes)', 'on_change_actions': ['reboot']},
                    'again_on_fail': {'human': 'Retry a different download after a failed one'}
                    }
    single = True

    def getCheckPathForPlatform(self, platform):
        if platform == common.WII:
            return self.c.check_path_wii
        elif platform == common.PS3:
            return self.c.check_path_ps3
        elif platform == common.XBOX360:
            return self.c.check_path_xbox360
        elif platform == common.PC:
            return self.c.check_path_pc

    def getBlacklistForPlatform(self, platform):
        out = ''
        if platform == common.WII:
            out = self.c.blacklist_wii
        elif platform == common.PS3:
            out = self.c.blacklist_ps3
        elif platform == common.XBOX360:
            out = self.c.blacklist_xbox360
        elif platform == common.PC:
            out = self.c.blacklist_pc
        return filter(None, out.split(','))
