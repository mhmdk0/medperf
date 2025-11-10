import builtins
from copy import deepcopy
import importlib
import threading
import os
import socket
import time
from medperf import config
from medperf.comms.auth.interface import Auth
from medperf.comms.rest import REST
from medperf.init import initialize
from medperf.ui.interface import UI
from medperf.web_ui.app import run
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from _pytest.assertion import truncate
from medperf.web_ui.app import web_app

HOST = "127.0.0.1"
PORT = 8100


truncate.DEFAULT_MAX_LINES = 9999
truncate.DEFAULT_MAX_CHARS = 9999


@pytest.fixture()
def disable_fs_IO_operations(monkeypatch):
    def stunted_walk():
        raise Exception("There was an attempt at walking through the filesystem")

    def stunted_open():
        raise Exception("There was an attempt at opening a file for IO")

    def stunted_exists():
        raise Exception("There was an attempt at checking the existence of a fs object")

    def stunted_remove():
        raise Exception("There was an attempt at removing a fs object")

    def stunted_chmod():
        raise Exception("There was an attempt at modifying a fs object permissions")

    def stunted_isdir():
        raise Exception(
            "There was an attempt at checking if a fs object is a directory"
        )

    def stunted_abspath():
        raise Exception("There was an attempt at converting a path to absolute")

    def stunted_mkdir():
        raise Exception("There was an attempt at creating a directory")

    def stunted_listdir():
        raise Exception("There was an attempt at listing a directory")

    monkeypatch.setattr(os, "walk", lambda *args, **kwargs: stunted_walk())
    monkeypatch.setattr(os, "remove", lambda *args, **kwargs: stunted_remove())
    monkeypatch.setattr(os, "chmod", lambda *args, **kwargs: stunted_chmod())
    monkeypatch.setattr(os, "mkdir", lambda *args, **kwargs: stunted_mkdir())
    monkeypatch.setattr(os, "makedirs", lambda *args, **kwargs: stunted_mkdir())
    monkeypatch.setattr(os, "listdir", lambda *args, **kwargs: stunted_listdir())
    monkeypatch.setattr(os.path, "isdir", lambda *args, **kwargs: stunted_isdir())
    # monkeypatch.setattr(os.path, "abspath", lambda *args, **kwargs: stunted_abspath())
    # monkeypatch.setattr(os.path, "exists", lambda *args, **kwargs: stunted_exists())
    monkeypatch.setattr(builtins, "open", lambda *args, **kwargs: stunted_open())


def _start_server():
    run(port=PORT)


@pytest.fixture(scope="session", autouse=True)
def webui_server():
    thread = threading.Thread(target=_start_server, daemon=True)
    thread.start()

    # wait for port
    for _ in range(50):
        try:
            with socket.create_connection((HOST, PORT), timeout=1):
                break
        except OSError:
            time.sleep(0.2)
    else:
        raise RuntimeError("WebUI did not start")

    yield f"http://{HOST}:{PORT}"


@pytest.fixture(scope="session", autouse=True)
def package_init():  # (fs) TODO
    # TODO: this might not be enough. Fixtures that don't depend on
    #       ui, auth, or comms may still run before this fixture
    #       all of this should hacky test setup be changed anyway
    orig_config_as_dict = {}
    try:
        orig_config = importlib.reload(config)
    except ImportError:
        orig_config = importlib.import_module("medperf.config", "medperf")
    for attr in dir(orig_config):
        if not attr.startswith("__"):
            orig_config_as_dict[attr] = deepcopy(getattr(orig_config, attr))
    initialize(for_webui=True)
    yield
    for attr in orig_config_as_dict:
        setattr(config, attr, orig_config_as_dict[attr])


@pytest.fixture
def ui(mocker, package_init):
    ui = mocker.create_autospec(spec=UI)
    config.ui = ui
    return ui


@pytest.fixture
def comms(mocker, package_init):
    comms = mocker.create_autospec(spec=REST)
    config.comms = comms
    return comms


@pytest.fixture
def auth(mocker, package_init):
    auth = mocker.create_autospec(spec=Auth)
    config.auth = auth
    return auth


@pytest.fixture
def driver_noauth():
    options = Options()
    options.add_argument("--headless=true")  # run without opening a real window
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def driver(sec_token):
    options = Options()
    options.add_argument("--headless=true")  # run without opening a real window
    driver = webdriver.Chrome(options=options)
    driver.get(f"http://127.0.0.1:8100/security_check?token={sec_token}")

    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def sec_token():
    from medperf.web_ui.auth import security_token

    return security_token


@pytest.fixture(autouse=True)
def reset_app():
    web_app.state.task_running = False
    web_app.state.task.running = False
    web_app.state.task.name = ""
    web_app.state.task.formData = {}
