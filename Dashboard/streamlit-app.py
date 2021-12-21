import pickle
import re

import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

import plotly.express as px

from multipage import *
from dashboardCalculations import *

# Config and setup
st.set_page_config(layout="wide", page_title="Transport Recommendation Dashboard", menu_items={
    'Get Help': 'https://plotly.com/python/parallel-coordinates-plot/',
    'About': "# App for the route recommendation. \n"
             "Version 0.1"
})

# References:
# 1. Streamlit multipage framework
# https://github.com/YanAlmeida/streamlit-multipage-framework


start_app()  # Clears the cache when the app is started

app = MultiPage()

app.start_button = "Let's start!"
app.navbar_name = "Navigation"

app.next_page_button = "Next Page"
app.previous_page_button = "Previous Page"

# Reading the dataset
routes_raw = pd.read_csv('../data.csv')
# routes_raw.rename({'sourcename': 'Source Name'}, axis=1, inplace=True)

# Extracting only unique and sorted lists of ODs
sources = routes_raw['sourcename'].sort_values().unique()
targets = routes_raw['targetname'].sort_values().unique()


def startpage():
    st.write("# Welcome :wave:")


def app1(prev_vars):  # First page

    # Questionnaire for the traveler to preconfigure filters

    with st.form("myform"):
        st.write("### Survey to provide you with the best recommendation")
        sourceName = st.selectbox('Origin', sources)
        targetName = st.selectbox('Destination', targets, index=1)
        # st.write("What is the most important value for you in your itinerary?")
        # preference = st.selectbox('Filter type', ('Price', 'Waiting Time'))
        travel_kids = st.selectbox('Do you travel with kids?', ('Yes', 'No'))

        if sourceName != targetName:

            if st.form_submit_button("Submit"):
                # Saving variables to use them on the recommendation page
                # save(var_list=[preference], name="Survey", page_names=["Dashboard"])
                save(var_list=[survey_pref_calc(travel_kids), sourceName, targetName], name="Survey",
                     page_names=["Dashboard"])
                change_page(1)
        else:
            st.error(
                'Recommendation cannot be done. Please select the destination that is different from the origin')


# Recommendation page
def app2(prev_vars):  # Second page
    st.write("# Transport Recommendation App")

    if prev_vars is not None:
        preference = prev_vars[0]
        sourceName = prev_vars[1]
        targetName = prev_vars[2]

        chosenODs = routes_raw.loc[
            (routes_raw["sourcename"] == sourceName) & (routes_raw.targetname == targetName)
            ]

        # Checking if survey was filled in
        if preference:

            best_recommendation_df = chosenODs[(chosenODs[preference] == chosenODs[preference].min())].head(1)
            st.write("The best recommendation (based on your survey):")
            st.write(best_recommendation_df["finalsolutionusedlabels"].to_string(index=False))

        else:
            return "### Please fill in the survey to get the best recommendation based on our algorithm"

        if not best_recommendation_df.empty:
            # st.write(best_recommendation_df["sourcename"].to_string(index=False))
            additional_recommendation_df = additional_recommendation(chosenODs, preference)

            comparison_best_additional = pd.concat([best_recommendation_df, additional_recommendation_df], axis=0)

            comparison_best_additional.reset_index(drop=True, inplace=True)

            comparison_best_additional = comparison_best_additional.assign(
                id=(comparison_best_additional['totalprice'].astype(str) + '_' + comparison_best_additional[
                    'totalwalkingdistanceinm'].astype(str)
                    + '_' + comparison_best_additional['totalnumberofchanges'].astype(str)
                    + '_' + comparison_best_additional['totaltraveltimeinhours'].astype(str)
                    + '_' + comparison_best_additional['totalwaitingtimeinhours'].astype(str))

                    .astype('category').cat.codes)

            comparison_best_additional['id'] = comparison_best_additional['id'].astype(np.int64)

            comparison_best_additional_fig = px.parallel_coordinates(
                comparison_best_additional,
                color="id",
                labels={"id": "Route", "totalprice": "Price",
                        "totalwalkingdistanceinm": "Walking Distance", "totalnumberofchanges": "Number of Changes",
                        "totaltraveltimeinhours": "Travel Time", "totalwaitingtimeinhours": "Waiting Time",
                        },
            )

            st.plotly_chart(comparison_best_additional_fig, use_container_width=True)


        else:
            st.warning("Unfortunately, there is no recommendation for the chosen itinerary. Please select another one")

    else:
        st.info("Please fill in the survey to get the best recommendation.")

    # Manual filtering section
    with st.expander('Manual filtering'):

        st.write("#### Configure filters and press the button to get the recommended mode for your choice")

        # Setting up filters
        sourceName = st.selectbox('Origin', sources)
        targetName = st.selectbox('Destination', targets, index=1)

        totalPrice = st.slider('Price (Euro)', 1, 59, (0, 59))
        totalNumberOfChanges = st.slider('Number of changes', 0, 7, (0, 7))
        totalWalkingDistance = st.slider('Walking distance (m)', 0, 965, (0, 965))
        totalWaitingTime = st.slider('Waiting time (h)', 0.0, 3.5, (0.0, 3.5), step=0.5)
        totalTravelTimeInHours = st.slider('Travel time (h)', 0.5, 4.5, (0.0, 4.5), step=0.5)

        # Recommending functionality
        if st.button('Recommend'):
            with st.spinner('Processing...'):

                if sourceName != targetName:

                    st.subheader('Recommendation')

                    chosenODs = routes_raw.loc[
                        (routes_raw.sourcename == sourceName) & (routes_raw.targetname == targetName)
                        & (routes_raw.totalprice >= totalPrice[0]) & (
                                routes_raw.totalprice <= totalPrice[1])
                        & (routes_raw.totalwalkingdistanceinm >= totalWalkingDistance[0]) & (
                                routes_raw.totalwalkingdistanceinm <= totalWalkingDistance[1])
                        & (routes_raw.totalnumberofchanges >= totalNumberOfChanges[0]) & (
                                routes_raw.totalnumberofchanges <= totalNumberOfChanges[1])
                        & (routes_raw.totaltraveltimeinhours >= totalTravelTimeInHours[0]) & (
                                routes_raw.totaltraveltimeinhours <= totalTravelTimeInHours[1])
                        & (routes_raw.totalwaitingtimeinhours >= totalWaitingTime[0]) & (
                                routes_raw.totalwaitingtimeinhours <= totalWaitingTime[1])
                        ]

                    chosenODs.reset_index(drop=True, inplace=True)

                    chosenODs = chosenODs.assign(
                        id=(chosenODs['totalprice'].astype(str) + '_' + chosenODs['totalwalkingdistanceinm'].astype(str)
                            + '_' + chosenODs['totalnumberofchanges'].astype(str)
                            + '_' + chosenODs['totaltraveltimeinhours'].astype(str)
                            + '_' + chosenODs['totalwaitingtimeinhours'].astype(str))

                            .astype('category').cat.codes)

                    chosenODs['id'] = chosenODs['id'].astype(np.int64)

                    st.write(chosenODs)
                    st.write(totalPrice)

                    # final_solutions = chosenODs['finalsolutionusedlabels']

                    # Make the transport labels look user-friendly
                    clean_recommendation = []

                    # for el in final_solutions:
                    #
                    #     clean_recommendation.append(re.sub(r"[\[\]]", "", el))
                    #
                    # # Output the recommendation
                    # for el in clean_recommendation:
                    #
                    #     st.write(el)

                    st.write('### Explanation of your recommendation')
                    st.info("* Drag the lines along the axes to filter regions.\n"
                            "* Double click on the axes releases selection.\n"
                            "* Drag different attributes for better comparison of choices.\n")
                    fig = px.parallel_coordinates(
                        chosenODs,
                        color="id",
                        labels={"id": "Route", "totalprice": "Price",
                                "totalwalkingdistanceinm": "Walking Distance",
                                "totalnumberofchanges": "Number of Changes",
                                "totaltraveltimeinhours": "Travel Time", "totalwaitingtimeinhours": "Waiting Time",
                                },
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    friendly_amount_lines = 7
                    if (len(chosenODs.index) > friendly_amount_lines):
                        st.info("Looks complicated? Please try to filter your preferences a bit more.")

                else:
                    st.error(
                        'Recommendation cannot be done. Please select the destination that is different from the origin')


# Page for the transport mode prediction using random forest model

def app3(prev_vars):  # Third page
    st.write("# Transport Prediction")

    st.write("#### Configure filters and press the button to get the recommended mode for your choice")

    # Setting up filters
    sourceName = st.selectbox('Origin', sources)
    targetName = st.selectbox('Destination', targets, index=1)
    totalPrice = st.slider('Price (Euro)', 1, 59, 0)
    totalNumberOfChanges = st.slider('Number of changes', 0, 7, 1)
    totalWalkingDistance = st.slider('Walking distance (m)', 0, 965, 200)
    totalWaitingTime = st.slider('Waiting time (h)', 0.0, 3.5, 0.0, step=0.5)
    totalTravelTimeInHours = st.slider('Travel time (h)', 0.5, 4.5, 3.0, step=0.5)

    # Accepting the user input
    def user_input_features(sourceName, targetName, totalPrice, totalNumberOfChanges, totalWalkingDistance,
                            totalWaitingTime, totalTravelTimeInHours):
        data = {
            'totaltraveltimeinhours': totalTravelTimeInHours,
            'totalprice': totalPrice,
            'totalnumberofchanges': totalNumberOfChanges,
            'totalwalkingdistanceinm': totalWalkingDistance,
            'totalwaitingtimeinhours': totalWaitingTime,
            'sourcename': sourceName,
            'targetname': targetName}
        features = pd.DataFrame(data, index=[0])
        return features

    # # Displays the user input features
    # st.subheader('User Input features')
    #
    # st.write(df)

    # Predicting functionality
    if st.button('Recommend'):
        # form.empty()
        with st.spinner('Processing...'):

            if sourceName != targetName:

                input_df = user_input_features(sourceName, targetName, totalPrice, totalNumberOfChanges,
                                               totalWalkingDistance,
                                               totalWaitingTime, totalTravelTimeInHours)

                # Combines user input features with entire routes dataset

                routes = routes_raw.drop(columns=['finalsolutionusedlabels'])
                df = pd.concat([input_df, routes], axis=0)

                # Encoding of ordinal features
                encode = ['objective', 'consideredpreferences', 'sourcename', 'targetname', 'finiteautomaton']
                for col in encode:
                    dummy = pd.get_dummies(df[col], prefix=col)
                    df = pd.concat([df, dummy], axis=1)
                    del df[col]
                df = df[:1]  # Selects only the first row (the user input data)

                # Reads in saved classification model
                load_clf = pickle.load(open('./routes_clf.pkl', 'rb'))

                # Apply model to make predictions
                prediction = load_clf.predict(df).astype(int)
                prediction_proba = load_clf.predict_proba(df)

                st.subheader('Prediction')

                # Extracting the mapped to the encoded values list of ODs
                ord_enc = OrdinalEncoder()
                routes_raw["finalsolutionusedlabels_code"] = ord_enc.fit_transform(
                    routes_raw[["finalsolutionusedlabels"]])

                ods_ordered_df = routes_raw.drop_duplicates(
                    subset=['finalsolutionusedlabels', 'finalsolutionusedlabels_code'])
                ods_ordered_df = ods_ordered_df[['finalsolutionusedlabels', 'finalsolutionusedlabels_code']]
                ods_ordered_df.sort_values(by=['finalsolutionusedlabels_code'], inplace=True)
                ods_ordered_lst = np.array(ods_ordered_df['finalsolutionusedlabels'])

                clean_prediction = re.sub(r"[\[\]]", "", ods_ordered_lst[prediction[0]])

                # Outputing the prediction
                st.write(f'{clean_prediction} :station:')

                # st.subheader('Prediction Probability')
                # st.write(prediction_proba)


            else:
                st.error(
                    'Recommendation cannot be done. Please select the destination that is different from the origin')


app.set_initial_page(startpage)
app.add_app("Survey", app1)
app.add_app("Dashboard", app2)
app.add_app("Prediction", app3)
app.run()
