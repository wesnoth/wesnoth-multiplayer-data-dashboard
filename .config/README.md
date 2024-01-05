# App Configuration

Create two files* in this folder:

`config.json`:

```json
{
    "url_base_pathname": "<your_url_base_pathname>",  // The pathname must start and end with "/". This field is optional and defaults to "/" when undeclared.
    "table_names_map": {
        "game_info": "<your_game_info_table>",
        "game_content_info": "<your_game_content_info_table>",
        "game_player_info": "<your_game_player_info_table>"
    }
}
```

`db_config.json`:

```json
{
    "user": "<your_username>",
    "password": "<your_password>",
    "host": "<your_host>",
    "port": <your_port>,
    "database": "<your_database>"
}
```

You can also use environment variables in place of `db_config.json`, as specified [here](../README.md#using-environment-variables-for-database-credentials-optional).

__*These files are not tracked in Git because they can contain sensitive information.__
