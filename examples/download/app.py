import asyncio
import os
import io
from datetime import date
from typing import Any

import shiny.ui_toolkit as st
from shiny import *
from htmltools import *

import matplotlib.pyplot as plt
import numpy as np


def make_example(id: str, label: str, title: str, desc: str, extra: Any = None):
    return st.column(
        4,
        div(
            class_="card mb-4",
            children=[
                div(title, class_="card-header"),
                div(
                    class_="card-body",
                    children=[
                        p(desc, class_="card-text text-muted"),
                        extra,
                        st.download_button(id, label, class_="btn-primary"),
                    ],
                ),
            ],
        ),
    )


ui = st.page_fluid(
    st.row(
        make_example(
            "download1",
            label="Download CSV",
            title="Simple case",
            desc="Downloads a pre-existing file, using its existing name on disk.",
        ),
    ),
    st.row(
        make_example(
            "download2",
            label="Download plot",
            title="Dynamic data generation",
            desc="Downloads a PNG that's generated on the fly.",
            extra=[
                st.input_text("title", "Plot title", "Random scatter plot"),
                st.input_slider("num_points", "Number of data points", 1, 100, 50),
            ],
        ),
    ),
    st.row(
        make_example(
            "download3",
            "Download",
            "Dynamic filename",
            "Demonstrates that filenames can be generated on the fly (and use Unicode characters!).",
        ),
    ),
    st.row(
        make_example(
            "download4",
            "Download",
            "Failed downloads",
            "Throws an error in the download handler, download should not succeed.",
        ),
    ),
    st.row(
        make_example(
            "download5",
            "Download",
            "Undefined download",
            "This button doesn't have corresponding server code registered to it, download should result in 404 error",
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @session.download()
    def download1():
        """
        This is the simplest case. The implementation simply returns the name of a file.
        Note that the function name (`download1`) determines which download_button()
        corresponds to this function.
        """

        path = os.path.join(os.path.dirname(__file__), "mtcars.csv")
        return path

    @session.download(filename="image.png")
    def download2():
        """
        Another way to implement a file download is by yielding bytes; either all at
        once, like in this case, or by yielding multiple times. When using this
        approach, you should pass a filename argument to @session.download, which
        determines what the browser will name the downloaded file.
        """

        x = np.random.uniform(size=session.input["num_points"])
        y = np.random.uniform(size=session.input["num_points"])
        plt.figure()
        plt.scatter(x, y)
        plt.title(input.title())
        with io.BytesIO() as buf:
            plt.savefig(buf, format="png")
            yield buf.getvalue()

    @session.download(
        filename=lambda: f"新型-{date.today().isoformat()}-{np.random.randint(100,999)}.csv"
    )
    async def download3():
        await asyncio.sleep(0.25)
        yield "one,two,three\n"
        yield "新,1,2\n"
        yield "型,4,5\n"

    @session.download(name="download4", filename="failuretest.txt")
    async def _():
        yield "hello"
        raise Exception("This error was caused intentionally")


app = App(ui, server)
