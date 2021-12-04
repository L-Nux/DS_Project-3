import pickle
import re

import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

import plotly.express as px

from multipage import *

# Config and setup
st.set_page_config(layout="wide", page_title="Transport Recommendation Dashboard")

# References:
# 1. Streamlit multipage framework
# https://github.com/YanAlmeida/streamlit-multipage-framework


start_app()  # Clears the cache when the app is started

app = MultiPage()

app.start_button = "Let's start!"
app.navbar_name = "Navigation"

app.next_page_button = "Next Page"
app.previous_page_button = "Previous Page"


def startpage():
    st.write("# Welcome :wave:")


def app1(prev_vars):  # First page

    # Questionnaire for the traveler to preconfigure filters

    with st.form("myform"):
        st.write("What is the most important value for you in your itinerary?")
        preference = st.selectbox('Filter type', ('Price', 'Waiting Time'))
        save(var_list=[preference], name="Survey", page_names=["Dashboard"])
        if st.form_submit_button("Submit"):
            change_page(1)

# Recommendation page
def app2(prev_vars):  # Second page
    st.write("# Transport Recommendation App")

    st.header('User Input Features')

    # Reading the dataset
    routes_raw = pd.read_csv('../data.csv')
    routes_raw.drop_duplicates(inplace = True)

    # dropping the instances with the same attributes for the different objectives
    routes_raw = routes_raw.drop_duplicates(subset=['totaltraveltimeinsec', 'totalprice', 'totalnumberofchanges',
                                    'totalwalkingdistance', 'totalwaitingtime', 'finiteautomaton',
                                    'finalsolutionusedlabels', 'sourcename', 'targetname'])

    # Extracting only unique and sorted lists of ODs
    sources = routes_raw['sourcename'].sort_values().unique()
    targets = routes_raw['targetname'].sort_values().unique()

    st.write("#### Configure filters and press the button to get the recommended mode for your choice")
    if prev_vars == 'Price':
        price_default = 0
        waiting_time_default = 1.0
    else:
        waiting_time_default = 0.0
        price_default = 20

    # Mechanism for additional routes propositions
    # Vars for additional route propositions
    step_number_changes = 1
    step_walking_distance = 50
    step_waiting_time = 0.5
    step_price = 10
    step_travel_time = 0.5

    # Setting up filters
    sourceName = st.selectbox('Origin', sources)
    targetName = st.selectbox('Destination', targets, index=1)


    totalPrice = st.slider('Price (Euro)', 1, 59, (0, 59))
    totalNumberOfChanges = st.slider('Number of changes', 0, 7, (0, 7))
    totalWalkingDistance = st.slider('Walking distance (m)', 0, 965, (0,965))
    totalWaitingTime = st.slider('Waiting time (h)', 0.0, 3.5, (0.0, 3.5), step=0.5)
    totalTravelTimeInSec = st.slider('Travel time (h)', 0.5, 4.5, (0.0,4.5), step=0.5)



    # Accepting the user input
    def user_input_features(sourceName, targetName, totalPrice, totalNumberOfChanges, totalWalkingDistance,
                            totalWaitingTime, totalTravelTimeInSec):
        data = {
            'totaltraveltimeinsec': totalTravelTimeInSec,
            'totalprice': totalPrice,
            'totalnumberofchanges': totalNumberOfChanges,
            'totalwalkingdistance': totalWalkingDistance,
            'totalwaitingtime': totalWaitingTime,
            'sourcename': sourceName,
            'targetname': targetName}
        features = pd.DataFrame(data, index=[0])
        return features

    # # Displays the user input features
    # st.subheader('User Input features')
    #
    # st.write(df)

    # Recommending functionality
    if st.button('Recommend'):
        # form.empty()
        with st.spinner('Processing...'):

            if sourceName != targetName:

                # input_df = user_input_features(sourceName, targetName, totalPrice, totalNumberOfChanges,
                #                                totalWalkingDistance,
                #                                totalWaitingTime, totalTravelTimeInSec)

                st.subheader('Recommendation')

                chosenODs = routes_raw.loc[(routes_raw.sourcename==sourceName) & (routes_raw.targetname==targetName)
                                           & (routes_raw.totalprice >= totalPrice[0]) & (routes_raw.totalprice <= totalPrice[1])
                                           & (routes_raw.totalwalkingdistance >= totalWalkingDistance[0]) & (routes_raw.totalwalkingdistance <= totalWalkingDistance[1])
                                           & (routes_raw.totalnumberofchanges >= totalNumberOfChanges[0]) & (
                                                       routes_raw.totalnumberofchanges <= totalNumberOfChanges[1])
                                           & (routes_raw.totaltraveltimeinsec >= totalTravelTimeInSec[0]) & (
                                                   routes_raw.totaltraveltimeinsec <= totalTravelTimeInSec[1])
                                           & (routes_raw.totalwaitingtime >= totalWaitingTime[0]) & (
                                                   routes_raw.totalwaitingtime <= totalWaitingTime[1])
                                           ]

                fig = px.parallel_coordinates(
                    chosenODs,

                    color_continuous_scale=px.colors.diverging.Tealrose,
                    color_continuous_midpoint=3)


                st.plotly_chart (fig, use_container_width=True)

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


                # st.write('Do you want to see adjusted propositions?')
                # if st.button('Yes!'):
                #     st.write('Choose the filter to adjust')
                #     st.selectbox('Filter type', ('Price, Waiting Time'))

                with st.expander('Explanation of your recommendation'):
                    st.write(
                        '- If you *increase waiting time for 1h* then it will be better to take **bla bla car** and then **flixbus**\n'
                        '- If you *increase traveling time time for 2h* then it will be better to take **train** and then **flixbus**')



            else:
                st.error(
                    'Recommendation cannot be done. Please select the destination that is different from the origin')


# Page for the transport mode prediction using random forest model

def app3(prev_vars):  # Third page
    st.write("# Transport Prediction")

    st.header('User Input Features')

    # Reading the dataset
    routes_raw = pd.read_csv('../data.csv')

    # Extracting only unique and sorted lists of ODs
    sources = routes_raw['sourcename'].sort_values().unique()
    targets = routes_raw['targetname'].sort_values().unique()

    st.write("#### Configure filters and press the button to get the recommended mode for your choice")

    # Setting up filters
    sourceName = st.selectbox('Origin', sources)
    targetName = st.selectbox('Destination', targets, index=1)
    totalPrice = st.slider('Price (Euro)', 1, 59, 0)
    totalNumberOfChanges = st.slider('Number of changes', 0, 7, 1)
    totalWalkingDistance = st.slider('Walking distance (m)', 0, 965, 200)
    totalWaitingTime = st.slider('Waiting time (h)', 0.0, 3.5, 0.0, step=0.5)
    totalTravelTimeInSec = st.slider('Travel time (h)', 0.5, 4.5, 3.0, step=0.5)

    # Accepting the user input
    def user_input_features(sourceName, targetName, totalPrice, totalNumberOfChanges, totalWalkingDistance,
                            totalWaitingTime, totalTravelTimeInSec):
        data = {
            'totaltraveltimeinsec': totalTravelTimeInSec,
            'totalprice': totalPrice,
            'totalnumberofchanges': totalNumberOfChanges,
            'totalwalkingdistance': totalWalkingDistance,
            'totalwaitingtime': totalWaitingTime,
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
                                               totalWaitingTime, totalTravelTimeInSec)
                # data = []
                #
                # for i in range(3):
                #     data.append((sourceName, targetName, totalPrice,
                #                  totalNumberOfChanges + step_number_changes,
                #                  totalWalkingDistance + step_walking_distance,
                #                  totalWaitingTime + step_waiting_time,
                #                  totalTravelTimeInSec + step_travel_time))
                #     step_number_changes += 1
                #     step_walking_distance += 50
                #     step_waiting_time += 0.5
                #     step_travel_time += 0.5
                #
                # dataf = pd.DataFrame(data)
                # st.write(dataf)
                #
                # i = 0
                # size = 2
                # while i < size:
                #     generate = user_input_features(sourceName, targetName, totalPrice,
                #                                    totalNumberOfChanges + step_number_changes,
                #                                    totalWalkingDistance + step_walking_distance,
                #                                    totalWaitingTime + step_waiting_time,
                #                                    totalTravelTimeInSec + step_travel_time)
                #
                #     input_df.append(generate)
                #
                #     combined = pd.concat([input_df, user_input_features(sourceName, targetName, totalPrice,
                #                                                         totalNumberOfChanges + step_number_changes,
                #                                                         totalWalkingDistance + step_walking_distance,
                #                                                         totalWaitingTime + step_waiting_time,
                #                                                         totalTravelTimeInSec + step_travel_time)],
                #                          ignore_index=True)
                #
                #     st.write(input_df)
                #
                #     i += 1
                #     step_number_changes += 1
                #     step_walking_distance += 50
                #     step_waiting_time += 0.5
                #     step_travel_time += 0.5
                #
                #     st.write(input_df)

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
