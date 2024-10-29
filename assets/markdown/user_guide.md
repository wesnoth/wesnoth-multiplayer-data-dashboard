This dashboard allows you to query and visualize data that the Wesnoth organization collects about multiplayer games played on the official server.

### Basic Usage

1. Begin by selecting a date range. Once you have selected a date range, data is fetched and the results are displayed in the figures.
2. You can hover over the figures to see more information about the data points. On a touch screen, the equivalent of hovering is to tap and hold.
3. When you hover over a figure, you will see a toolbar in its top right corner. You can use this toolbar to zoom in, zoom out, pan, autoscale, and reset the axes. More information about the toolbar can be found [here](https://plotly.com/chart-studio-help/getting-to-know-the-plotly-modebar/).

### Advanced Usage of the Query Table

The data of the table found in the Query Page can be manipulated in a number of ways These manipulations are performed clientside (in the browser) and do not result in database queries or commits. The only time the database is queried is when the date range is changed. Whenever the state of the table changes, the visualizations and values in the dashboard are updated to reflect the changes. To reset the table to its original state, refresh the page and start again.

#### Sorting

You can sort the table by ascending or descending order by clicking on the up and down arrow icons on the left side of the column name in the column headers.

#### Filtering

There is a cell below the column headers that can be used to filter the table data. A special filtering syntax is used. See the full [filter syntax reference](https://dash.plotly.com/datatable/filtering).

To get started, there are four filters you can use:
1. equality: `=`
2. contains a substring: `contains`
3. partial datetime match: `datestartswith`
4. a group of comparison operators: `>, >=, <, <=, !=`

By default, if you only type a value with no operator, depending on the data type of the column, the filter might default to `contains` for string columns and `=` for numeric columns. To be more sure your filtering is correct, you could use the operators explicitly.

Here are some examples that have been tested:
1. Filter for games that contain OOS using `=0` on the OOS column.
2. Filter for games longer than 50 minutes using `>50` on the `GAME_DURATION` column.
3. Filter for games using version 1.16 using `contains1.16` on the `INSTANCE_VERSION` column.

#### Editing Cell Values

You can edit the values in individual cells by selecting any cell and typing. Note that there is no blinking cursor that appears when you select a cell; just start typing and the value will change.

#### Deleting Rows

Rows can be deleted by clicking on the 'x' icon in the first column of the table.

### Note on the Histogram in the Query Page

The first bin of the histogram is centered on the minimum value of the dataset. What this means, for example, is that in a dataset whose lowest value is 0, the lower end (left edge) of the bin will start at a negative value. This is not the same as the default behavior in some other apps, such as Excel, and is a [conscious design decision by Plotly](https://github.com/plotly/plotly.py/issues/3771).
