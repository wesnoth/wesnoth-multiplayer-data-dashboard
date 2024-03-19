import pytest
from dash.exceptions import PreventUpdate

from app import (
    toggle_user_guide_modal,
    update_instance_version_chart,
    update_oos_chart,
    update_reload_chart,
    update_observers_chart,
    update_password_chart,
    update_public_chart,
    update_total_games_value,
)


class TestUpdateTotalGamesValue:
    def test_returns_table_length_given_a_date_range(self):
        # Arrange
        start_date = "2022-02-01"
        end_date = "2022-02-28"
        expected_total_games_value = ("1,373", 1373)

        # Act
        total_games_value = update_total_games_value(start_date, end_date)

        # Assert
        assert total_games_value == expected_total_games_value

    def test_returns_0_given_empty_table_data(self):
        # Arrange
        start_date = "2023-12-01"
        end_date = "2023-12-22"
        expected_total_games_value = ("0", 0)

        # Act
        total_games_value = update_total_games_value(start_date, end_date)

        # Assert
        assert total_games_value == expected_total_games_value

    @pytest.mark.parametrize(
        "start_date, end_date",
        [(None, None), (None, "2022-01-02"), ("2022-01-01", None)],
    )
    def test_any_missing_dates_raises_prevent_update(self, start_date, end_date):
        with pytest.raises(PreventUpdate):
            update_total_games_value(start_date, end_date)


def test_update_instance_version_chart_returns_a_pie_figure_given_a_date_range():
    # Arrange
    start_date = "2022-02-01"
    end_date = "2022-02-28"
    expected_figure_trace_type = "pie"

    # Act
    figure = update_instance_version_chart(start_date, end_date)

    # Assert
    assert figure["data"][0].type == expected_figure_trace_type


def test_update_oos_chart_returns_a_pie_figure_given_a_date_range():
    # Arrange
    start_date = "2022-02-01"
    end_date = "2022-02-28"
    expected_figure_trace_type = "pie"

    # Act
    figure = update_oos_chart(start_date, end_date)

    # Assert
    assert figure["data"][0].type == expected_figure_trace_type


def test_update_reload_chart_returns_a_pie_figure_given_a_date_range():
    # Arrange
    start_date = "2022-02-01"
    end_date = "2022-02-28"
    expected_figure_trace_type = "pie"

    # Act
    figure = update_reload_chart(start_date, end_date)

    # Assert
    assert figure["data"][0].type == expected_figure_trace_type


def test_update_observers_chart_returns_a_pie_figure_given_a_date_range():
    # Arrange
    start_date = "2022-02-01"
    end_date = "2022-02-28"
    expected_figure_trace_type = "pie"

    # Act
    figure = update_observers_chart(start_date, end_date)

    # Assert
    assert figure["data"][0].type == expected_figure_trace_type


def test_update_password_chart_returns_a_pie_figure_given_a_date_range():
    # Arrange
    start_date = "2022-02-01"
    end_date = "2022-02-28"
    expected_figure_trace_type = "pie"

    # Act
    figure = update_password_chart(start_date, end_date)

    # Assert
    assert figure["data"][0].type == expected_figure_trace_type


def test_update_public_chart_returns_a_pie_figure_given_a_date_range():
    # Arrange
    start_date = "2022-02-01"
    end_date = "2022-02-28"
    expected_figure_trace_type = "pie"

    # Act
    figure = update_public_chart(start_date, end_date)

    # Assert
    assert figure["data"][0].type == expected_figure_trace_type


@pytest.mark.parametrize(
    "user_guide_button_clicks, close_button_clicks, is_modal_open, expected_is_modal_open",
    [
        # Test that clicking the user guide button opens the modal
        (1, None, False, True),
        # Test that clicking the close button closes the modal
        (None, 1, True, False),
        # Test that the modal remains closed if no buttons are clicked
        (None, None, False, False),
        # Test that the modal remains open if it was already open and no buttons are clicked
        (None, None, True, True),
        # Test that clicking both buttons opens the modal
        (1, 1, False, True),
        # Test that clicking both buttons closes the modal
        (1, 1, True, False),
    ],
)
def test_toggle_modal(
    user_guide_button_clicks, close_button_clicks, is_modal_open, expected_is_modal_open
):
    assert (
        toggle_user_guide_modal(user_guide_button_clicks, close_button_clicks, is_modal_open)
        == expected_is_modal_open
    )
