import pytest
from dash.exceptions import PreventUpdate
from pandas import NaT, Timestamp, isna

from app import (toggle_modal, update_game_duration_histogram,
                 update_instance_version_chart, update_observers_chart,
                 update_oos_chart, update_password_chart, update_public_chart,
                 update_reload_chart, update_table, update_total_games_value)


class TestUpdateTable:
    def test_valid_dates_and_data_returns_list_of_records_with_a_derived_game_duration_field(self, mocker):
        # Patch the database connection and cursor
        mock_connect_to_mariadb = mocker.patch('app.connect_to_mariadb')
        mock_connection = mocker.Mock()
        mock_cursor = mocker.Mock()
        mock_connect_to_mariadb.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None

        # Fake schema
        mock_cursor.description = [
            ('INSTANCE_UUID', None),
            ('GAME_ID', None),
            ('INSTANCE_VERSION', None),
            ('GAME_NAME', None),
            ('START_TIME', None),
            ('END_TIME', None),
            ('REPLAY_NAME', None),
            ('OOS', None),
            ('RELOAD', None),
            ('OBSERVERS', None),
            ('PASSWORD', None),
            ('PUBLIC', None)
        ]

        # Fake data
        mock_cursor.fetchall.return_value = [(
            '3f29e05d-8b16-11ec-81a2-0ee77816ca01',
            4892,
            '1.16',
            'Partie de Kema_Eka',
            # datetime(2022, 2, 17, 21, 22, 46),
            # datetime(2022, 2, 17, 21, 25, 46),
            '2022-02-17 21:22:46',
            '2022-02-17 21:25:46',
            None,
            0,
            0,
            1,
            1,
            1
        )]

        # Query date range
        start_date = '2022-02-01'
        end_date = '2022-02-28'

        expected_table_data = [
            {
                'INSTANCE_UUID': '3f29e05d-8b16-11ec-81a2-0ee77816ca01',
                'GAME_ID': 4892,
                'INSTANCE_VERSION': '1.16',
                'GAME_NAME': 'Partie de Kema_Eka',
                'START_TIME': Timestamp('2022-02-17 21:22:46'),
                'END_TIME': Timestamp('2022-02-17 21:25:46'),
                'REPLAY_NAME': None,
                'OOS': 0,
                'RELOAD': 0,
                'OBSERVERS': 1,
                'PASSWORD': 1,
                'PUBLIC': 1,
                'GAME_DURATION': 3  # the unit is in minutes
            }
        ]

        # Act
        table_data = update_table(start_date, end_date)

        # Assert
        assert table_data == expected_table_data

    def test_null_start_and_end_times_results_in_a_null_game_duration(self, mocker):
        # Patch the database connection and cursor
        mock_connect_to_mariadb = mocker.patch('app.connect_to_mariadb')
        mock_connection = mocker.Mock()
        mock_cursor = mocker.Mock()
        mock_connect_to_mariadb.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None

        # Fake schema
        mock_cursor.description = [
            ('START_TIME', None),
            ('END_TIME', None),
        ]

        # Fake data
        mock_cursor.fetchall.return_value = [(
            NaT,
            NaT,
        )]

        # Query date range
        start_date = '2022-02-01'
        end_date = '2022-02-28'

        # Act
        table_data = update_table(start_date, end_date)

        # Assert
        assert isna(table_data[0]['GAME_DURATION'])

    @pytest.mark.parametrize(
        "start_date, end_date",
        [
            (None, None),
            (None, '2022-01-02'),
            ('2022-01-01', None)
        ]
    )
    def test_any_missing_dates_raises_prevent_update(self, start_date, end_date):
        with pytest.raises(PreventUpdate):
            update_table(start_date, end_date)


def test_update_instance_version_chart_returns_a_pie_figure_given_table_columns_and_data():
    # Arrange
    fake_data = [
        {'INSTANCE_VERSION': '1.16', 'RELOAD': 0},
        {'INSTANCE_VERSION': '1.16', 'RELOAD': 1},
        {'INSTANCE_VERSION': '1.14', 'RELOAD': 0},
    ]
    fake_columns = [
        {'name': 'INSTANCE_VERSION', 'id': 'INSTANCE_VERSION'},
        {'name': 'RELOAD', 'id': 'RELOAD'}
    ]
    expected_figure_trace_type = 'pie'

    # Act
    figure = update_instance_version_chart(fake_data, fake_columns)

    # Assert
    assert figure['data'][0].type == expected_figure_trace_type


def test_update_oos_chart_returns_a_pie_figure_given_table_columns_and_data():
    # Arrange
    fake_data = [
        {'OOS': 0, 'RELOAD': 0},
        {'OOS': 1, 'RELOAD': 1},
        {'OOS': 0, 'RELOAD': 0},
    ]
    fake_columns = [
        {'name': 'OOS', 'id': 'OOS'},
        {'name': 'RELOAD', 'id': 'RELOAD'}
    ]
    expected_figure_trace_type = 'pie'

    # Act
    figure = update_oos_chart(fake_data, fake_columns)

    # Assert
    assert figure['data'][0].type == expected_figure_trace_type


def test_update_reload_chart_returns_a_pie_figure_given_table_columns_and_data():
    # Arrange
    fake_data = [
        {'RELOAD': 0, 'OOS': 0},
        {'RELOAD': 1, 'OOS': 1},
        {'RELOAD': 0, 'OOS': 0},
    ]
    fake_columns = [
        {'name': 'RELOAD', 'id': 'RELOAD'},
        {'name': 'OOS', 'id': 'OOS'}
    ]
    expected_figure_trace_type = 'pie'

    # Act
    figure = update_reload_chart(fake_data, fake_columns)

    # Assert
    assert figure['data'][0].type == expected_figure_trace_type


def test_update_observers_chart_returns_a_pie_figure_given_table_columns_and_data():
    # Arrange
    fake_data = [
        {'OBSERVERS': 0, 'RELOAD': 0},
        {'OBSERVERS': 1, 'RELOAD': 1},
        {'OBSERVERS': 0, 'RELOAD': 0},
    ]
    fake_columns = [
        {'name': 'OBSERVERS', 'id': 'OBSERVERS'},
        {'name': 'RELOAD', 'id': 'RELOAD'}
    ]
    expected_figure_trace_type = 'pie'

    # Act
    figure = update_observers_chart(fake_data, fake_columns)

    # Assert
    assert figure['data'][0].type == expected_figure_trace_type


def test_update_password_chart_returns_a_pie_figure_given_table_columns_and_data():
    # Arrange
    fake_data = [
        {'PASSWORD': 0, 'RELOAD': 0},
        {'PASSWORD': 1, 'RELOAD': 1},
        {'PASSWORD': 0, 'RELOAD': 0},
    ]
    fake_columns = [
        {'name': 'PASSWORD', 'id': 'PASSWORD'},
        {'name': 'RELOAD', 'id': 'RELOAD'}
    ]
    expected_figure_trace_type = 'pie'

    # Act
    figure = update_password_chart(fake_data, fake_columns)

    # Assert
    assert figure['data'][0].type == expected_figure_trace_type


def test_update_public_chart_returns_a_pie_figure_given_table_columns_and_data():
    # Arrange
    fake_data = [
        {'PUBLIC': 0, 'RELOAD': 0},
        {'PUBLIC': 1, 'RELOAD': 1},
        {'PUBLIC': 0, 'RELOAD': 0},
    ]
    fake_columns = [
        {'name': 'PUBLIC', 'id': 'PUBLIC'},
        {'name': 'RELOAD', 'id': 'RELOAD'}
    ]
    expected_figure_trace_type = 'pie'

    # Act
    figure = update_public_chart(fake_data, fake_columns)

    # Assert
    assert figure['data'][0].type == expected_figure_trace_type


def test_update_game_duration_histogram_returns_a_histogram_figure_given_table_columns_and_data():
    # Arrange
    fake_data = [
        {'GAME_DURATION': 3, 'RELOAD': 0},
        {'GAME_DURATION': 4.57, 'RELOAD': 1},
        {'GAME_DURATION': 0, 'RELOAD': 0},
        {'GAME_DURATION': 1.5, 'RELOAD': 0},
        {'GAME_DURATION': 1000, 'RELOAD': 0},
    ]
    fake_columns = [
        {'name': 'GAME_DURATION', 'id': 'GAME_DURATION'},
        {'name': 'RELOAD', 'id': 'RELOAD'}
    ]
    expected_figure_trace_type = 'histogram'

    # Act
    figure = update_game_duration_histogram(fake_data, fake_columns)

    # Assert
    assert figure['data'][0].type == expected_figure_trace_type


class TestUpdateTotalGamesValue:
    def test_returns_table_length_given_table_data(self):
        # Arrange
        fake_data = [
            {'GAME_DURATION': 3, 'RELOAD': 0},
            {'GAME_DURATION': 4.57, 'RELOAD': 1},
            {'GAME_DURATION': 0, 'RELOAD': 0},
            {'GAME_DURATION': 1.5, 'RELOAD': 0},
            {'GAME_DURATION': 1000, 'RELOAD': 0},
        ]
        expected_total_games_value = '5'

        # Act
        total_games_value = update_total_games_value(fake_data)

        # Assert
        assert total_games_value == expected_total_games_value

    def test_returns_0_given_empty_table_data(self):
        # Arrange
        fake_data = []
        expected_total_games_value = '0'

        # Act
        total_games_value = update_total_games_value(fake_data)

        # Assert
        assert total_games_value == expected_total_games_value

    def test_return_value_contains_thousand_separators_when_table_length_exceeds_a_thousand(self):
        # Arrange
        fake_data = [{} for _ in range(1001)]
        expected_total_games_value = '1,001'

        # Act
        total_games_value = update_total_games_value(fake_data)

        # Assert
        assert total_games_value == expected_total_games_value

    def test_raises_prevent_update_when_table_data_is_none(self):
        with pytest.raises(PreventUpdate):
            update_total_games_value(None)


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
    ]
)
def test_toggle_modal(user_guide_button_clicks, close_button_clicks, is_modal_open, expected_is_modal_open):
    assert toggle_modal(user_guide_button_clicks, close_button_clicks,
                        is_modal_open) == expected_is_modal_open
