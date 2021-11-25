import pickle
import re

import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

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
        st.session_state.preference = st.selectbox('Filter type', ('Price', 'Waiting Time'))

        if st.form_submit_button("Submit"):
            change_page(1)


def app2(prev_vars):  # Second page
    st.write("# Routes Prediction App")

    st.header('User Input Features')

    # Reading the dataset
    routes_raw = pd.read_csv('./data.csv')

    # Extracting only unique and sorted lists of ODs
    sources = routes_raw['sourcename'].sort_values().unique()
    targets = routes_raw['targetname'].sort_values().unique()

    st.write("#### Configure filters and press the button to get the recommended mode for your choice")

    if st.session_state.preference == 'Price':
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
    totalPrice = st.slider('Price (Euro)', 0, 59, price_default)
    totalNumberOfChanges = st.slider('Number of changes', 0, 7, 1)
    totalWalkingDistance = st.slider('Walking distance (m)', 0, 965, 200)
    totalWaitingTime = st.slider('Waiting time (h)', 0.0, 3.5, waiting_time_default, step=0.5)
    totalTravelTimeInSec = st.slider('Travel time (h)', 0.0, 4.5, 3.0, step=0.5)

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

                i = 0
                size = 2
                while i < size:
                    generate = user_input_features(sourceName, targetName, totalPrice,
                                                   totalNumberOfChanges + step_number_changes,
                                                   totalWalkingDistance + step_walking_distance,
                                                   totalWaitingTime + step_waiting_time,
                                                   totalTravelTimeInSec + step_travel_time)
                    input_df.append(generate)
                    # combined = pd.concat([input_df,user_input_features(sourceName, targetName, totalPrice, totalNumberOfChanges + step_number_changes,
                    #                                     totalWalkingDistance + step_walking_distance,
                    #                                     totalWaitingTime + step_waiting_time, totalTravelTimeInSec + step_travel_time)], ignore_index=True)
                    # st.write(input_df)
                    i += 1
                    step_number_changes += 1
                    step_walking_distance += 50
                    step_waiting_time += 0.5
                    step_travel_time += 0.5
                # st.write(input_df)

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

                st.subheader('Recommendation')

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

                # A bit of a celebration mood
                # st.balloons()

                # st.subheader('Prediction Probability')
                # st.write(prediction_proba)

                # st.write('Do you want to see adjusted propositions?')
                # if st.button('Yes!'):
                #     st.write('Choose the filter to adjust')
                #     st.selectbox('Filter type', ('Price, Waiting Time'))

                # st.success('Your recommendation is ready!')

                with st.expander('Explanation of your recommendation'):
                    st.write('#### Here goes the explanation')



            else:
                st.error(
                    'Recommendation cannot be done. Please select the destination that is different from the origin')



app.set_initial_page(startpage)
app.add_app("Survey", app1)  # Adds first page (app1) to the framework
app.add_app("Dashboard", app2)  # Adds second page (app2) to the framework
app.run()  # Runs the multipage app!
