import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier

st.write("# Routes Prediction App")

st.sidebar.header('User Input Features')

routes_raw = pd.read_csv('combined_csv_2dim.csv')

sources = routes_raw['sourceName'].unique()
targets = routes_raw['targetName'].unique()

sourceName = st.sidebar.selectbox('Origin', sources)
targetName = st.sidebar.selectbox('Destination', targets)
totalPrice = st.sidebar.slider(' Price', 0,59,362)
totalNumberOfChanges = st.sidebar.slider('Number of changes', 0,7)
totalWalkingDistance = st.sidebar.slider('Walking distance', 0.0,0.5,0.96485)
totalWaitingTime = st.sidebar.slider('Waiting time', 0,6300,76630)
totalTravelTimeInSec = st.sidebar.slider('Travel time (seconds)', 424,6300,89987)

def user_input_features(sourceName,targetName,totalPrice, totalNumberOfChanges, totalWalkingDistance,totalWaitingTime,totalTravelTimeInSec):

    data = {
            'totalTravelTimeInSec': totalTravelTimeInSec,
                'totalPrice': totalPrice,
                'totalNumberOfChanges': totalNumberOfChanges,
                'totalWalkingDistance': totalWalkingDistance,
                'totalWaitingTime': totalWaitingTime,
                'sourceName': sourceName,
                'targetName': targetName}
    features = pd.DataFrame(data, index=[0])
    return features



# # Displays the user input features
# st.subheader('User Input features')
#
# st.write(df)

st.write("### Press the button to get the recommended mode for your choice")

if st.sidebar.button('Predict'):

    input_df = user_input_features(sourceName, targetName, totalPrice, totalNumberOfChanges, totalWalkingDistance,
                                   totalWaitingTime, totalTravelTimeInSec)

    # Combines user input features with entire routes dataset

    routes = routes_raw.drop(columns=['finiteAutomaton'])
    df = pd.concat([input_df, routes], axis=0)

    # Encoding of ordinal features
    encode = ['objective', 'consideredPreferences', 'sourceName', 'targetName', 'finalSolutionUsedLabels']
    for col in encode:
        dummy = pd.get_dummies(df[col], prefix=col)
        df = pd.concat([df, dummy], axis=1)
        del df[col]
    df = df[:1]  # Selects only the first row (the user input data)

    # Reads in saved classification model
    load_clf = pickle.load(open('routes_clf.pkl', 'rb'))

    # Apply model to make predictions
    prediction = load_clf.predict(df)
    prediction_proba = load_clf.predict_proba(df)


    st.subheader('Prediction')
    automata_pred = np.array(['all', 'ptOnly', 'noFlights'])
    st.write(automata_pred[prediction])

    st.subheader('Prediction Probability')
    st.write(prediction_proba)


