import pickle

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.preprocessing import OrdinalEncoder

st.write("# Routes Prediction App")

st.sidebar.header('User Input Features')

# Reading the dataset
routes_raw = pd.read_csv('data.csv')

# Extracting only unique and sorted lists of ODs
sources = routes_raw['sourcename'].sort_values().unique()
targets = routes_raw['targetname'].sort_values().unique()

# Setting up the sidebar
sourceName = st.sidebar.selectbox('Origin', sources)
targetName = st.sidebar.selectbox('Destination', targets)
totalPrice = st.sidebar.slider('Price', 0, 59, 362)
totalNumberOfChanges = st.sidebar.slider('Number of changes', 0, 7)
totalWalkingDistance = st.sidebar.slider('Walking distance', 0.0, 0.5, 0.96485)
totalWaitingTime = st.sidebar.slider('Waiting time', 0, 6300, 76630)
totalTravelTimeInSec = st.sidebar.slider('Travel time', 0, 260)


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


st.write("### Press the button to get the recommended mode for your choice")

# Predicting functionality
if st.sidebar.button('Predict'):

    input_df = user_input_features(sourceName, targetName, totalPrice, totalNumberOfChanges, totalWalkingDistance,
                                   totalWaitingTime, totalTravelTimeInSec)

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
    load_clf = pickle.load(open('routes_clf.pkl', 'rb'))

    # Apply model to make predictions
    prediction = load_clf.predict(df).astype(int)
    prediction_proba = load_clf.predict_proba(df)

    st.subheader('Prediction')

    # Extracting the mapped to the encoded values list of ODs
    ord_enc = OrdinalEncoder()
    routes_raw["finalsolutionusedlabels_code"] = ord_enc.fit_transform(routes_raw[["finalsolutionusedlabels"]])

    ods_ordered_df = routes_raw.drop_duplicates(subset=['finalsolutionusedlabels', 'finalsolutionusedlabels_code'])
    ods_ordered_df = ods_ordered_df[['finalsolutionusedlabels', 'finalsolutionusedlabels_code']]
    ods_ordered_df.sort_values(by=['finalsolutionusedlabels_code'], inplace=True)
    ods_ordered_lst = np.array(ods_ordered_df['finalsolutionusedlabels'])

    # Outputing the prediction
    st.write(ods_ordered_lst[prediction[0]])

    # A bit of a celebration mood
    st.balloons()

    st.subheader('Prediction Probability')
    st.write(prediction_proba)
