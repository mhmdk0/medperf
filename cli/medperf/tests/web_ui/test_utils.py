import pytest

from medperf.web_ui.utils import strip_ansi


@pytest.mark.parametrize(
    "text, expected",
    [
        ("\x1b[1;31mred\x1b[0m text", "red text"),
        ("no colors", "no colors"),
        (None, ""),
    ],
)
def test_strip_ansi_removes_terminal_styles(text, expected):
    # Act
    result = strip_ansi(text)

    # Assert
    assert result == expected
