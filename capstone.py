import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="COVID-19 Country Dashboard",
    layout="wide"
)

st.title("COVID-19 Country Dashboard")
st.write(
    "Explore confirmed COVID-19 cases and deaths by country using "
    "data from the Johns Hopkins University CSSE COVID-19 Dashboard."
)

# Data URLs
confirmed_url = (
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"
    "csse_covid_19_data/csse_covid_19_time_series/"
    "time_series_covid19_confirmed_global.csv"
)

deaths_url = (
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"
    "csse_covid_19_data/csse_covid_19_time_series/"
    "time_series_covid19_deaths_global.csv"
)


@st.cache_data
def load_data(url):
    return pd.read_csv(url)


@st.cache_data
def clean_data(data):
    date_columns = data.columns[4:]

    country_data = (
        data.groupby("Country/Region")[date_columns]
        .sum()
        .transpose()
    )

    country_data.index = pd.to_datetime(country_data.index)
    country_data.index.name = "Date"

    return country_data


confirmed_raw = load_data(confirmed_url)
deaths_raw = load_data(deaths_url)

confirmed = clean_data(confirmed_raw)
deaths = clean_data(deaths_raw)


# User options
countries = st.multiselect(
    "Select countries",
    options=confirmed.columns.tolist(),
    default=["US"]
)

metric = st.selectbox(
    "Select measure",
    ["Confirmed Cases", "Deaths"]
)

count_type = st.radio(
    "Select count type",
    ["Daily", "Cumulative"],
    horizontal=True
)


# Choose dataset
if metric == "Confirmed Cases":
    data = confirmed
else:
    data = deaths


if countries:
    selected_data = data[countries].copy()

    if count_type == "Daily":
        selected_data = selected_data.diff().fillna(0)

    # Convert to long format for Plotly
    plot_data = selected_data.reset_index()

    plot_data = plot_data.melt(
        id_vars="Date",
        var_name="Country",
        value_name="Count"
    )

    fig = px.line(
        plot_data,
        x="Date",
        y="Count",
        color="Country",
        title=f"{count_type} {metric}"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Cases"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Latest values
    st.subheader("Latest reported values")

    latest = selected_data.iloc[-1]

    for country in countries:
        st.write(
            country + ":",
            f"{latest[country]:,.0f}"
        )

else:
    st.info("Please select at least one country.")


st.divider()

st.caption(
    "Data source: Johns Hopkins University Center for Systems Science "
    "and Engineering (JHU CSSE) COVID-19 Dashboard. "
    "The repository contains historical data through March 2023."
)

st.caption(
    "Daily values are calculated as the difference between consecutive "
    "cumulative reports. Negative daily values may appear when historical "
    "data were corrected or revised."
)