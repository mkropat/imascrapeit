import contextlib, json, os.path

from selenium import webdriver

from .browser import Browser, DownloadWatcher

@contextlib.contextmanager
def open_chrome(profile_dir, quit=True):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['ignore-certificate-errors'])
    options.add_argument(r'user-data-dir=%s' % profile_dir)

    driver = webdriver.Chrome('chromedriver', chrome_options=options)
    try:
        yield Browser(driver, lambda: _ChromeDownloadWatcher(profile_dir))
    finally:
        if quit:
            driver.quit()

class _ChromeDownloadWatcher:
    def __init__(self, profile_dir):
        download_dir = self._get_download_dir(profile_dir)
        self._watcher = DownloadWatcher(download_dir)

    def wait(self):
        return self._watcher.wait_until_not(['.crdownload', '.tmp'])

    @staticmethod
    def _get_download_dir(profile_dir):
        try:
            preferences_path = os.path.join(profile_dir, 'Default', 'Preferences')
            with open(preferences_path) as preferences_file:
                prefs = json.load(preferences_file)
                return prefs['download']['default_directory']
        except Exception:
            home_dir = os.path.expanduser('~')
            return os.path.join(home_dir, 'Downloads')

