# Management wants some interactive insights at their fingertips ASAP on how we performed last year (2023) in some large cities: Amsterdam, Rotterdam & Groningen.

# Specifically, we are interested in:

# - The average number of reviews per day in these cities
# - The number of reviews per day over time in these cities
# - Filtering the time window for all graphs

import datetime as dt
import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOSTNAME = os.environ["DB_HOSTNAME"]
DB_NAME = os.environ["DB_NAME"]

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:5432/{DB_NAME}")

## 1


@st.cache_data
def load():
    df = pd.read_sql_query(
        """
    select
        DATE(datetime) as review_date,
        location_city,
        count(*) as n_reviews,
        AVG(rating_delivery) as avg_del_score,
        AVG(rating_food) as avg_food_score
    from
        reviews revs
    left join
    restaurants rests
    on
        revs.restaurant_id = rests.restaurant_id
    where
        datetime >= '2023-01-01'
        and datetime < '2024-01-01'
        and location_city in ('Groningen', 'Amsterdam', 'Rotterdam')
    group by
        DATE(datetime),
        location_city
    """,
        con=engine,
    )
    return df


df_reviews = load()

st.title("Performance in 2023 in Rotterdam, Amsterdam and Groningen")

# The average number of reviews per day in each city (calculated as one number per city over the entire year)
avg_reviews = df_reviews.groupby(["location_city"], as_index=False)["n_reviews"].mean()

st.subheader("Average Number of Reviews Per Day in Rotterdam, Groningen and Amsterdam")

st.bar_chart(avg_reviews, x="location_city", y="n_reviews")


## 2

# Convert the review_date to datetime
df_reviews["review_date"] = pd.to_datetime(df_reviews["review_date"])
df_reviews = df_reviews.sort_values("review_date")


##2.1
st.subheader("The Number of Reviews Per Day in Rotterdam, Groningen and Amsterdam")

# user date input
start_date = st.date_input(
    "Choose your Start date",
    value=dt.date(2023, 1, 1),
    min_value=dt.date(2023, 1, 1),
    max_value=dt.date(2023, 12, 31),
    format="YYYY-MM-DD",
)
end_date = st.date_input(
    "Choose your End date",
    value=dt.date(2023, 1, 31),
    min_value=dt.date(2023, 1, 1),
    max_value=dt.date(2023, 12, 31),
    format="YYYY-MM-DD",
)

window_1 = df_reviews[
    (df_reviews["review_date"].dt.date > start_date) & (df_reviews["review_date"].dt.date < end_date)
]

st.line_chart(
    window_1,
    x="review_date",
    y="n_reviews",
    color="location_city",
    x_label="Number of reviews",
    y_label="Time",
)


##2.2
st.subheader("The Number of Reviews Per Day Per City")
# City selection
cities = df_reviews["location_city"].unique()
selected_city = st.selectbox("Select a city", cities)

# Filter the data based on the selected city
city_data = df_reviews[df_reviews["location_city"] == selected_city]

# Window selection
start_date_1 = st.date_input(
    f"Choose your Start date for {selected_city}",
    value=dt.date(2023, 1, 1),
    min_value=dt.date(2023, 1, 1),
    max_value=dt.date(2023, 12, 31),
    format="YYYY-MM-DD",
)
end_date_1 = st.date_input(
    f"Choose your Start date for {selected_city}",
    value=dt.date(2023, 1, 31),
    min_value=dt.date(2023, 1, 1),
    max_value=dt.date(2023, 12, 31),
    format="YYYY-MM-DD",
)

window_2 = city_data[
    (city_data["review_date"].dt.date > start_date_1) & (city_data["review_date"].dt.date < end_date_1)
]

# find function to display graph
st.line_chart(window_2, x="review_date", y="n_reviews", x_label="Number of reviews", y_label="Time")
