# This will load the shiny module dynamically, without having to install it.
# This makes the debug/run cycle quicker.
import os
import sys

shiny_module_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, shiny_module_dir)


from shiny import *
from htmltools import tags, HTML

ui = page_fluid(
    panel_title("Hello prism ui"),
    layout_sidebar(
        panel_sidebar(
            input_slider("n", "input_slider()", 0, 100, 50),
            input_date("date", "input_date()"),
            input_date_range("date_rng", "input_date_range()"),
            input_text("txt", "input_text()", placeholder="Input some text"),
            input_text_area(
                "txt_area", "input_text_area()", placeholder="Input some text"
            ),
            input_checkbox("checkbox", "input_checkbox()"),
            input_checkbox_group(
                "checkbox_group",
                "input_checkbox_group()",
                {"Choice 1": "a", "Choice 2": "b"},
                selected="b",
                inline=True,
            ),
            input_radio_buttons(
                "radio", "input_radio()", {"Choice 1": "a", "Choice 2": "b"}
            ),
        ),
        panel_main(
            output_plot("plot"),
            output_ipywidget("IntSlider"),
            output_ipywidget("ipyleaflet"),
            navs_tab_card(
                # TODO: output_plot() within a tab not working?
                nav("Inputs", output_ui("inputs")),
                nav("Image", output_image("image", inline=True)),
                nav(
                    "Misc",
                    input_link("link", "Show notification/progress"),
                    # TODO: fix these
                    # input_file("file", "File upload"),
                    # input_button("btn", "Show modal")
                    panel_fixed(
                        panel_well(
                            "A fixed, draggable, panel",
                            input_checkbox("checkbox2", "Check me!"),
                            panel_conditional(
                                "input.checkbox2 == true", "Thanks for checking!"
                            ),
                        ),
                        draggable=True,
                        width="fit-content",
                        height="50px",
                        top="50px",
                        right="50px",
                    ),
                ),
            ),
        ),
    ),
)


import numpy as np
import matplotlib.pyplot as plt


def server(ss: ShinySession):
    @ss.output("inputs")
    @render.ui()
    def _() -> Tag:
        vals = [
            f"<code>input_date()</code> {ss.input['date']}",
            f"<code>input_date_range()</code>: {ss.input['date_rng']}",
            f"<code>input_text()</code>: {ss.input['txt']}",
            f"<code>input_text_area()</code>: {ss.input['txt_area']}",
            f"<code>input_checkbox()</code>: {ss.input['checkbox']}",
            f"<code>input_checkbox_group()</code>: {ss.input['checkbox_group']}",
            f"<code>input_radio()</code>: {ss.input['radio']}",
        ]
        return tags.pre(HTML("\n".join(vals)))

    @ss.output("plot")
    @render.plot(alt="A histogram")
    def _():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)
        fig, ax = plt.subplots()
        ax.hist(x, ss.input["n"], density=True)
        return fig

    @ss.output("image")
    @render.image()
    def _():
        from pathlib import Path

        dir = Path(__file__).resolve().parent
        return {"src": dir / "rstudio-logo.png", "width": "150px"}

    @observe()
    def _():
        btn = ss.input["btn"]
        if btn and btn > 0:
            modal_show(modal("Hello there!", easy_close=True))

    @observe()
    def _():
        link = ss.input["link"]
        if link and link > 0:
            notification_show("A notification!")
            p = Progress()
            import time

            for i in range(30):
                p.set(i / 30, message="Computing")
                time.sleep(0.1)
            p.close()


app = ShinyApp(ui, server)
if __name__ == "__main__":
    app.run()
