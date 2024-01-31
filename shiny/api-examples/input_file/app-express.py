import pandas as pd

from shiny import reactive
from shiny.express import input, render, ui
from shiny.types import FileInfo

ui.input_file("file1", "Choose CSV File", accept=[".csv"], multiple=False)
ui.input_checkbox_group(
    "stats",
    "Summary Stats",
    choices=["Row Count", "Column Count", "Column Names"],
    selected=["Row Count", "Column Count", "Column Names"],
)


@reactive.Calc
def parsed_file():
    file: list[FileInfo] | None = input.file1()
    if file is None:
        return pd.DataFrame()
    return pd.read_csv(file[0]["datapath"])  # pyright: ignore[reportUnknownMemberType]


@render.table
def summary():
    df = parsed_file()

    if df.empty:
        return pd.DataFrame()

    # Get the row count, column count, and column names of the DataFrame
    row_count = df.shape[0]
    column_count = df.shape[1]
    names = df.columns.tolist()
    column_names = ", ".join(str(name) for name in names)

    # Create a new DataFrame to display the information
    info_df = pd.DataFrame(
        {
            "Row Count": [row_count],
            "Column Count": [column_count],
            "Column Names": [column_names],
        }
    )

    # input.stats() is a list of strings; subset the columns based on the selected
    # checkboxes
    return info_df.loc[:, input.stats()]
