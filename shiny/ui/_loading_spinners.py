from __future__ import annotations

from typing import Literal, Optional

from htmltools import HTMLDependency, Tag, head_content, tags


def use_loading_spinners(
    type: Literal["tadpole", "disc", "dots", "dot-track", "bounce"] = "tadpole",
    color: Optional[str] = None,
    size: Optional[str] = None,
    speed: Optional[str] = None,
    delay: Optional[str] = None,
) -> HTMLDependency:
    """
    Function to tweak loading spinner options for app.

    This function allows you to tweak the style of the loading spinners used in your app.

    When supplied in your app's UI, elements that are loading (e.g. plots or tables)
    will have a spinner displayed over them. This is useful for when you have a
    long-running computation and want to indicate to the user that something is
    happening beyond the default grayed-out element.

    Parameters
    ----------

    type
        The type of spinner to use. Options include "tadpole", "disc", "dots",
        "dot-track", and "bounce". Defaults to "tadpole".
    color
        The color of the spinner. This can be any valid CSS color. Defaults to the
        current app "primary" color (if using a theme) or light-blue if not.
    size
        The size of the spinner. This can be any valid CSS size. Defaults to "40px".
    speed
        The amount of time for the spinner to complete a single revolution. This can be
        any valid CSS time. Defaults to "2s".
    delay
        The amount of time to wait before showing the spinner. This can be any valid CSS
        time. Defaults to "0.1s". This is useful for not showing the spinner if the
        computation finishes quickly.

    Returns
    -------
    :
        An HTMLDependency

    Notes
    -----
    This function is meant to be called a single time. If it is called multiple times
    with different arguments then only the first call will be reflected.
    """

    animation = None
    easing = None

    # Some of the spinners work better with linear easing and some with ease-in-out so
    # we modify them together.
    if type == "disc":
        svg = "disc-spinner.svg"
        easing = "linear"
    elif type == "dots":
        svg = "dots-spinner.svg"
        easing = "linear"
    elif type == "dot-track":
        svg = "dot-track-spinner.svg"
        easing = "linear"
    elif type == "bounce":
        svg = "ball.svg"
        animation = "shiny-loading-spinner-bounce"
        # Set speed variable to 0.8s if it hasnt been set by the user
        speed = speed or "0.8s"
    else:
        svg = "tadpole-spinner.svg"
        easing = "linear"

    # We set options using css variables. Here we create the rule that updates the
    # appropriate variables before being included in the head of the document with our
    # html dep.
    rule_contents = (
        f"--shiny-spinner-svg: url({svg});"
        + (f"--shiny-spinner-easing: {easing};" if easing else "")
        + (f"--shiny-spinner-animation: {animation};" if animation else "")
        + (f"--shiny-spinner-color: {color};" if color else "")
        + (f"--shiny-spinner-size: {size};" if size else "")
        + (f"--shiny-spinner-speed: {speed};" if speed else "")
        + (f"--shiny-spinner-delay: {delay};" if delay else "")
    )

    return head_content(tags.style(HTML("body{" + rule_contents + "}</style>")))

def with_spinner(el: Tag) -> Tag:
    """
    Enable a loading spinner for a given output. These spinners will sit directly on the
    output itself rather than in the upper corner.

    Parameters
    ----------

    el
        The element to add the spinner to. Typically an output element like a
        plot or table.

    Returns
    -------
    :
        Element with the class "show-spinner" added to it.

    Examples
    --------

    ```{python}
    #|eval: false
    ui.with_spinner(ui.output_plot("plot")),
    ```
    """
    el.attrs["class"] = el.attrs.get("class", "") + " show-spinner"
    return el
