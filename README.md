# Wesnoth Multiplayer Data Dashboard

## Setup for Development

Install development dependencies using

```bash
pip install -r requirements/development.txt
```

## App Observability

The [Callback Graph](https://dash.plotly.com/devtools#callback-graph) makes it easy to track app state, app data, callback function call counts, and callback function execution time.

## Testing

### Keystone Functions

As far as unit tests are concerned, the most critical keystone function to have a variety of test cases for is the `update_table()` callback function because this function is the one that fetches a larger amount of raw data from a database, converts the data to a pandas dataframe, conditions the data, and derives additional features from the data.

The output target of this function, the table, is then used by the other callback functions to generate the graphs and charts, so whether this function does its job properly determines the successful or failed outcome of the next callbacks.
