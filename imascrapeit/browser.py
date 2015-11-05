import contextlib, datetime, os, os.path, random, time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from watchdog.observers import Observer
from watchdog.events import FileCreatedEvent, FileSystemEventHandler

from .duration import seconds

class Browser:
    def __init__(self, driver, download_watcher_factory):
        self._driver = driver
        self._watcher_factory = download_watcher_factory
        self._watcher = None

        self._driver.implicitly_wait(10) # seconds

    @property
    def url(self):
        return self._driver.current_url

    def load(self, url):
        self._driver.get(url)

        self._delay()

    def click(self, selector):
        el = self._find(selector)
        el.click()

        self._delay()

    def input_text(self, selector, text):
        field = self._find(selector)
        field.send_keys(text)

    def input_text_submit(self, selector, text):
        field = self._find(selector)
        field.send_keys(text)
        field.send_keys(Keys.RETURN)

        self._delay()

    def override_text(self, selector, text):
        self.wait_for(selector)
        self._driver.execute_script("""
        var el = document.querySelector('%s');
        el.value = '%s'""" % (selector, text))

    def get_text(self, selector):
        el = self._find(selector)
        if el.text:
            return el.text.strip()

    def exists_element(self, selector):
        return self._find(selector) is not None

    def wait_for(self, selector, timeout=None):
        if timeout is None:
            self._find(selector)
        else:
            timeout = seconds(timeout)
            selector_match = expected_conditions.presence_of_element_located((By.CSS_SELECTOR, selector))
            WebDriverWait(self._driver, timeout.total_seconds()).until(selector_match)

    def execute(self, script):
        return self._driver.execute_script(script)

    @contextlib.contextmanager
    def enter_iframe(self, selector):
        try:
            self._driver.switch_to.frame(self._find(selector))
            yield
        finally:
            self._driver.switch_to.default_content()

    def watch_download_dir(self):
        if not self._watcher:
            self._watcher = self._watcher_factory()

    @contextlib.contextmanager
    def open_download(self):
        path = self._watcher.wait()
        self._watcher = None

        try:
            with open(path) as f:
                yield f
        finally:
            if path:
                os.remove(f)

    def _find(self, selector):
        return self._driver.find_element_by_css_selector(selector)

    def _delay(self):
        num_seconds = abs(random.normalvariate(0, 1))
        time.sleep(num_seconds)

class DownloadWatcher:
    def __init__(self, dir_path):
        self.file_watcher = _FirstFileCreationHandler()
        self.observer = Observer()
        self.observer.schedule(self.file_watcher, path=dir_path)
        self.observer.start()

    def wait_until_not(self, ignored_extensions):
        try:
            while not self.file_watcher.path or \
                    self.matches_extension(self.file_watcher.path, ignored_extensions):
                time.sleep(0.1)
        finally:
            self.observer.stop()

        return self.file_watcher.path

    @staticmethod
    def matches_extension(path, extensions):
        _, ext = os.path.splitext(path)
        return ext in extensions

class _FirstFileCreationHandler(FileSystemEventHandler):
    def __init__(self):
        self.path = None

    def on_created(self, event):
        if not self.path and not event.is_directory:
            self.path = event.src_path

    def on_moved(self, event):
        if self.path and self.path == event.src_path:
            self.path = event.dest_path
