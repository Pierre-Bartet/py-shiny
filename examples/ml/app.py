import json

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.h3("Dynamic output"),
    ui.ml.output_classification_label("label1"),
    ui.input_slider("lion", "Lion value:", min=0, max=100, value=60, step=1),
    ui.h3("Static output", style="margin-top: 3rem;"),
    ui.ml.output_classification_label(
        "label2",
        value={
            "Tigers": 32,
            "Lions": 60,
            "Bears": 15,
        },
    ),
    ui.h3("Static output, sort=False"),
    ui.ml.output_classification_label(
        "label3",
        value={
            "Tigers": 32,
            "Lions": 60,
            "Bears": 15,
        },
        sort=False,
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.text
    def label1():
        return json.dumps(
            {
                "Tigers": 32,
                "Lions": input.lion(),
                "Bears": 15,
            },
        )


app = App(app_ui, server)
