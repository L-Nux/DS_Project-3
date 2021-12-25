import operator
import streamlit as st


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


# Indicator showing the extent to which the search results change due to an adjustment of the filters
def indicator_calculation(feature, filterTuple, df_initial, df_filtered):
    increase_indicator = 5

    if df_initial[feature].max() > filterTuple[1] or df_initial[feature].min() < filterTuple[0]:

        if (len(df_initial.index) - len(df_filtered.index)) >= increase_indicator and (len(df_initial.index) - len(df_filtered.index)) < increase_indicator*2:

            st.write(f"{feature} :arrow_up:")

        elif (len(df_initial.index) - len(df_filtered.index)) >= increase_indicator * 2 and (len(df_initial.index) - len(df_filtered.index)) < increase_indicator * 3:

            st.write(f"{feature} :arrow_up: :arrow_up:")
        elif (len(df_initial.index) - len(df_filtered.index)) >= increase_indicator * 3:
            st.write(f"{feature} :arrow_up: :arrow_up: :arrow_up:")

