from types import SimpleNamespace

from medperf.web_ui import settings


def make_request(auto_give_access):
    state = SimpleNamespace(model_auto_give_access=auto_give_access)
    return SimpleNamespace(app=SimpleNamespace(state=state))


def test_activate_profile_is_refused_while_auto_grant_access_runs(mocker):
    read_config = mocker.patch.object(settings, "read_config")
    request = make_request({"1_2": {"running": True}})

    response = settings.activate_profile(request, profile="other", current_user=True)

    assert response["status"] == "failed"
    assert "Automatic grant access" in response["error"]
    read_config.assert_not_called()


def test_activate_profile_switches_profile(mocker):
    config_p = mocker.MagicMock()
    config_p.__contains__.return_value = True
    mocker.patch.object(settings, "read_config", return_value=config_p)
    write_config = mocker.patch.object(settings, "write_config")
    initialize = mocker.patch.object(settings, "initialize")

    response = settings.activate_profile(make_request({}), profile="other", current_user=True)

    assert response["status"] == "success"
    config_p.activate.assert_called_once_with("other")
    write_config.assert_called_once_with(config_p)
    initialize.assert_called_once_with(for_webui=True)
