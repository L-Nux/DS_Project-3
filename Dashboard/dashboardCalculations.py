import operator
import streamlit as st
import numpy as np
import plotly.express as px


# Preference calculation based on survey
def survey_pref_calc(travel_kids):
    preference = {
        "totalprice": 0,
        "totalwaitingtimeinhours": 0,
        "totaltraveltimeinhours": 0,
        "totalwalkingdistanceinm": 0,
        "numberoftransfers": 0
    }

    if travel_kids == "Yes":
        preference["totalprice"] += 0.5
        preference["totalwaitingtimeinhours"] += 0.9
        preference["totaltraveltimeinhours"] += 0.9
        preference["totalwalkingdistanceinm"] += 1
        preference["numberoftransfers"] += 1
    else:
        preference["totalprice"] += 0.7
        preference["totalwaitingtimeinhours"] += 0.5
        preference["totaltraveltimeinhours"] += 0.5
        preference["totalwalkingdistanceinm"] += 0.5
        preference["numberoftransfers"] += 0.5

    return max(preference.items(), key=operator.itemgetter(1))[0]


# Function for generating additional recommendations
def additional_recommendation(df, preference):
    minvalue = df[preference].min()

    threshold = 0.25

    additional_recommendation_df = df.loc[(df[preference] > minvalue) & (df[preference] <= (minvalue + threshold))]

    while additional_recommendation_df.empty:

        threshold += 0.25
        additional_recommendation_df = df.loc[(df[preference] > minvalue) & (df[preference] <= (minvalue + threshold))]
        if not additional_recommendation_df.empty:
            additional_recommendation_df.drop_duplicates(subset=["finalsolutionusedlabels"], inplace=True)
            st.write(f"When the __{preference}__ is __{threshold}__ units, the features of your trip and "
                     f"the transport you should choose are the next (Route 1 on the diagram):")
            st.write(additional_recommendation_df["finalsolutionusedlabels"].to_string(index=False))
            break
    return additional_recommendation_df


# TODO: make the feature name look nice
# Indicator showing the extent to which the search results change due to an adjustment of the filters
def indicator_calculation(feature, filterTuple, df_initial, df_filtered):
    increase_indicator = 5

    if df_initial[feature].max() > filterTuple[1] or df_initial[feature].min() < filterTuple[0]:

        if (len(df_initial.index) - len(df_filtered.index)) >= increase_indicator and (
                len(df_initial.index) - len(df_filtered.index)) < increase_indicator * 2:

            st.write(f"{feature} :arrow_up:")

        elif (len(df_initial.index) - len(df_filtered.index)) >= increase_indicator * 2 and (
                len(df_initial.index) - len(df_filtered.index)) < increase_indicator * 3:

            st.write(f"{feature} :arrow_up: :arrow_up:")
        elif (len(df_initial.index) - len(df_filtered.index)) >= increase_indicator * 3:
            st.write(f"{feature} :arrow_up: :arrow_up: :arrow_up:")


# Assigning unique ids to the rows
def assign_ids(df):
    df_with_ids = df.assign(
        id=(df['totalprice'].astype(str) + '_' + df[
            'totalwalkingdistanceinm'].astype(str)
            + '_' + df['totaltraveltimeinhours'].astype(str)
            + '_' + df['totalwaitingtimeinhours'].astype(str)
            + '_' + df['safety_boost'].astype(str)
            + '_' + df['caloriesBurnt_avg'].astype(str))
            .astype('category').cat.codes)
    df_with_ids['id'] = df_with_ids['id'].astype(np.int64)

    return df_with_ids


def draw_parallel_coord(df):
    return px.parallel_coordinates(
        df,
        color="id",
        labels={"id": "Route", "totalprice": "Price",
                "totalwalkingdistanceinm": "Walking Distance",
                "totaltraveltimeinhours": "Travel Time", "totalwaitingtimeinhours": "Waiting Time",
                },
    )


# Showing the indicators
def show_indicators(df_filtered, df, filters):
    for feature, filter1 in zip(df_filtered, filters):

        if df_filtered.dtypes[feature] == np.float64 or df_filtered.dtypes[
            feature] == np.int64:
            indicator_calculation(feature, filter1, df, df_filtered)

    # TODO: output it only when the indicator appears
    st.info("* 1 arrow = if you adjust this feature a few of additional recommendations appear \n"
            "* 2 arrows = if you adjust this feature a dozen of additional recommendations appear \n"
            "* 3 arrows = if you adjust this feature a lot of additional recommendations appear \n")


def check_amount_lines(df_filtered, amount_lines):
    if (len(df_filtered.index) > amount_lines):
        st.info("Looks complicated? Please try to filter your preferences a bit more.")


# def change_in_filter(filter_initial_upper_value, filter_initial_lower_value, filter_tuple):
#     if filter_initial_upper_value != filter_tuple[1] or filter_initial_lower_value != filter_tuple[0]:
#         st.write(filter_initial_upper_value)
#         st.write(filter_tuple[1])
#         return True
