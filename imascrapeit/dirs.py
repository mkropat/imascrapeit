import os, os.path

if os.name == 'nt':
    def chrome_profile(name):
        return os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data', name)

    def settings():
        return os.path.join(os.environ['LOCALAPPDATA'], 'ImaScrapeIt')

if os.name == 'posix':
    def chrome_profile(name):
        return os.path.join(os.path.expanduser('~'), '.config', 'google-chrome', name)

    def settings():
        return os.path.join(os.path.expanduser('~'), '.imascrapeit')
