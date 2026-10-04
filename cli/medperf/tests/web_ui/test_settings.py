from types import SimpleNamespace

from medperf import config
from medperf.web_ui import settings

PATCH_SETTINGS = "medperf.web_ui.settings.{}"


def make_request(auto_give_access):
    state = SimpleNamespace(model_auto_give_access=auto_give_access)
    return SimpleNamespace(app=SimpleNamespace(state=state))


def test_activate_profile_is_refused_while_auto_grant_access_runs(mocker):
    # Arrange
    read_config = mocker.patch(PATCH_SETTINGS.format("read_config"))
    request = make_request({"1-2": {"name": "benchmark"}})

    # Act
    response = settings.activate_profile(request, profile="other", current_user=True)

    # Assert
    assert response["status"] == "failed"
    assert "Automatic grant access" in response["error"]
    read_config.assert_not_called()


def test_activate_profile_switches_profile_and_its_history(mocker):
    # Arrange
    config_p = mocker.MagicMock()
    config_p.__contains__.return_value = True
    mocker.patch(PATCH_SETTINGS.format("read_config"), return_value=config_p)
    write_config = mocker.patch(PATCH_SETTINGS.format("write_config"))
    initialize = mocker.patch(PATCH_SETTINGS.format("initialize"))
    ui = mocker.patch.object(config, "ui")

    # Act
    response = settings.activate_profile(
        make_request({}), profile="other", current_user=True
    )

    # Assert
    assert response["status"] == "success"
    config_p.activate.assert_called_once_with("other")
    write_config.assert_called_once_with(config_p)
    initialize.assert_called_once_with(for_webui=True)
    ui.load_history.assert_called_once()
