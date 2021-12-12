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
            additional_recommendation_df.drop_duplicates(subset=["finalsolutionusedlabels"], inplace = True)
            st.write(f"If you increase __{preference}__ by __{threshold}__ units you can consider taking next options:")
            st.write(additional_recommendation_df["finalsolutionusedlabels"].to_string(index=False))
            break
    return additional_recommendation_df