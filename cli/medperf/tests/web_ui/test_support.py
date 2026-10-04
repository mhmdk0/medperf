import os

import pytest
from fastapi import HTTPException

from medperf import config
from medperf.web_ui import support


def test_read_last_lines_returns_only_the_last_lines(fs):
    fs.create_file("/logs/app.log", contents="one\ntwo\nthree\nfour\n")

    assert support.read_last_lines("/logs/app.log", 2) == ["three", "four"]


def test_read_last_lines_of_missing_file_is_empty(fs):
    assert support.read_last_lines("/logs/missing.log", 10) == []


def test_support_info_returns_clean_latest_log_lines(fs, mocker):
    mocker.patch.object(config, "logs_storage", "/logs")
    mocker.patch.object(config, "webui_max_log_messages", 2)
    mocker.patch.object(config, "webui_support_emails", ["support@example.com"])
    log_file = os.path.join("/logs", config.webui_log_file)
    fs.create_file(log_file, contents="old\n\x1b[31merror\x1b[0m\nlast\n")

    info = support.support_info(current_user=True)

    assert info["emails"] == ["support@example.com"]
    assert info["log_file"] == log_file
    assert info["log_lines"] == ["error", "last"]
    assert info["environment"]["MedPerf version"]


def test_download_logs_returns_the_logs_package(fs, mocker):
    mocker.patch.object(config, "logs_storage", "/logs")
    package = os.path.join("/logs", config.log_package_file)
    mocker.patch.object(
        support, "package_logs", side_effect=lambda: fs.create_file(package)
    )

    response = support.download_logs(current_user=True)

    assert response.path == package
    assert response.filename == config.log_package_file


def test_download_logs_without_logs_is_not_found(fs, mocker):
    mocker.patch.object(config, "logs_storage", "/logs")
    mocker.patch.object(support, "package_logs")

    with pytest.raises(HTTPException) as e:
        support.download_logs(current_user=True)

    assert e.value.status_code == 404
