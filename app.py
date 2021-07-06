#!/usr/bin/env python3
"""Quick MyFitnessPal helper app."""

# import plotly.graph_objects as go
import plotly.io
import pandas as pd
import streamlit as st
import datetime
import myfitnesspal
import statsmodels
import plotly.express as px
from dateutil.relativedelta import relativedelta
from typing import Optional, Tuple, Dict, Any

plotly.io.templates.default = "seaborn"

st.title("PyFitnessPal")


@st.cache()
def MFP_dict_to_df(weight_dict: Dict[str, Any]) -> pd.DataFrame:
    """Convert dict returned from myfitnesspal.get_measurements to DataFrame.

    Args:
        weight_dict (Dict[Any]): ordered dict of date and weight measurements.

    Returns:
        pd.DataFrame: dataframe of date and weight measurements."""
    df = pd.DataFrame.from_dict(weight_dict, orient="index")
    df = df.reset_index().rename(columns={"index": "Date", 0: "Weight"})

    return df


@st.cache()
def new_plot_with_trend(
    df: pd.DataFrame, start: Optional[str] = None, end: Optional[str] = None, **kwargs
) -> Tuple[float]:
    """Quick plot of MFP data with trendline.

    Args:
        df (pd.DataFrame): dataframe of date/weight data
        start (str, optional): start date to graph
        end (str, optional): end date to graph

    Returns:
        Tuple[float]: m and b for 'y = mx + b'
    """

    if start:
        dt_start = datetime.datetime.strptime(start, "%Y-%m-%d").date()
        df = df[df.Date > dt_start]
    if end:
        dt_end = datetime.datetime.strptime(end, "%Y-%m-%d").date()
        df = df[df.Date < dt_end]

    new_df = df.copy()
    new_df.Date = new_df.Date.apply(lambda x: datetime.datetime(x.year, x.month, x.day))

    fig = px.line(new_df, x="Date", y="Weight", **kwargs)
    fig2 = px.scatter(
        new_df.iloc[:14],
        x="Date",
        y="Weight",
        trendline="ols",
        trendline_color_override="red",
    )
    fig.add_trace(fig2.data[1])
    results = px.get_trendline_results(fig2)
    # results.px_fit_results.iloc[0].summary()
    m = results.px_fit_results.iloc[0].params[1]
    b = results.px_fit_results.iloc[0].params[0]

    now = datetime.datetime.now()
    new_time = now + relativedelta(days=+14)
    new_weight = m * new_time.timestamp() + b

    fig.add_annotation(
        text=f"Weight in two weeks: {new_weight:.1f} lbs",
        xref="paper",
        yref="paper",
        x=0.9,
        y=1.1,
        showarrow=False,
    )

    return fig


@st.cache()
def get_MFP_weights(user: str, MFP_pass: str, date: datetime.date) -> Any:
    client = myfitnesspal.Client(user, password=MFP_pass)
    weight = client.get_measurements("Weight", date)
    return weight


start_date = datetime.date(2021, 5, 25)

st.sidebar.header("Variables")

user = st.sidebar.text_input("MFP Username", "Paradoxdruid")
MFP_pass = st.sidebar.text_input("MFP Password")

if st.sidebar.button("Process"):
    weight = get_MFP_weights(user, MFP_pass, start_date)
    df = MFP_dict_to_df(weight)
    fig = new_plot_with_trend(
        df, start="2021-05-25", end="2021-08-01", title="Weight Loss"
    )

    st.plotly_chart(fig)

st.sidebar.markdown(
    """--------\nMade by [Andrew J. Bonham](https://github.com/Paradoxdruid)"""
)
