import pytest

from prep_workflow.graph import Graph
from prep_workflow.main import _check_registered, main


def _graph(statistics_step="Statistics"):
    return Graph.from_spec(
        {
            "steps": [
                {
                    "id": "setup",
                    "step": "Setup",
                    "per_subject": False,
                    "next": None,
                },
                {
                    "id": "sanity_check",
                    "step": "SanityCheck",
                    "per_subject": False,
                    "next": "statistics",
                },
                {
                    "id": "statistics",
                    "step": statistics_step,
                    "per_subject": False,
                    "next": None,
                },
            ],
        }
    )


def test_valid_workflow_passes():
    steps = {"Setup": object(), "SanityCheck": object(), "Statistics": object()}
    _check_registered(_graph(), steps, {})


def test_sanity_check_flow_must_include_statistics():
    steps = {"Setup": object(), "SanityCheck": object(), "Other": object()}
    with pytest.raises(SystemExit, match="Statistics"):
        _check_registered(_graph(statistics_step="Other"), steps, {})


def test_prepare_flow_must_stop_before_validation_steps():
    graph = _graph()
    graph.node("setup").nxt = "sanity_check"
    steps = {"Setup": object(), "SanityCheck": object(), "Statistics": object()}
    with pytest.raises(SystemExit, match="stop before validation"):
        _check_registered(graph, steps, {})


def test_sanity_check_step_id_is_required():
    graph = Graph.from_spec(
        {
            "steps": [
                {
                    "id": "setup",
                    "step": "Setup",
                    "per_subject": False,
                    "next": None,
                }
            ]
        }
    )
    with pytest.raises(SystemExit, match="sanity_check"):
        _check_registered(graph, {"Setup": object()}, {})


@pytest.mark.parametrize(
    "argv,expected_start,expected_resume",
    [
        ([], "prepare", True),
        (["--start=sanity_check"], "sanity_check", False),
    ],
)
def test_main_selects_start(mocker, argv, expected_start, expected_resume):
    engine = mocker.Mock()
    mocker.patch("prep_workflow.main.build_engine", return_value=engine)

    main(argv)

    engine.run.assert_called_once_with(expected_start, resume=expected_resume)
