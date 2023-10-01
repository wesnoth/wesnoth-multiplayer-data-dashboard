import pytest
from dash.exceptions import PreventUpdate
from pandas import Timestamp

from app import update_table


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
                'GAME_DURATION': 3
            }
        ]

        # Act
        table_data = update_table(start_date, end_date)

        # Assert
        assert table_data == expected_table_data

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
