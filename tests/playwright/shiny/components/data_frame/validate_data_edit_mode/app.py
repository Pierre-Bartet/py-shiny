from palmerpenguins import load_penguins_raw  # pyright: ignore[reportMissingTypeStubs]

from shiny import App, Inputs, Outputs, Session, render, ui
from shiny.render._dataframe import CellPatch
from shiny.types import SafeException

app_ui = ui.page_fluid(
    ui.h2("Palmer Penguins"),
    ui.output_data_frame("penguins_df"),
    ui.output_code("selected_row_count"),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    @render.data_frame
    def penguins_df():
        return render.DataGrid(
            data=load_penguins_raw(),  # pyright: ignore[reportUnknownArgumentType]
            filters=True,
            editable=True,
        )

    @render.code
    def selected_row_count():
        # grid_selected_data = grid_selected.data()
        return str(
            penguins_df.data_selected()  # pyright: ignore[reportUnknownMemberType]
        )

    @penguins_df.set_patch_fn
    async def upgrade_patch(
        *,
        patch: CellPatch,
    ):
        print(patch)
        if (patch["column_index"] == 4) and (
            patch["value"] not in ["Torgersen", "Biscoe", "Dream"]
        ):  # check island
            raise SafeException(
                "Penguin island should be one of 'Torgersen', 'Biscoe', 'Dream'"
            )
        if (patch["column_index"] == 9) and int(
            patch["value"]
        ) > 50:  # check culmen length
            raise SafeException("Penguin culmen length cannot be greater than 50mm")
        return patch["value"]


app = App(app_ui, server)
