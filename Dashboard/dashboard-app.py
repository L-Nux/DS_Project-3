import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier

st.write("""
# Routes Prediction App
""")

st.sidebar.header('User Input Features')

def user_input_features():

    sourceName = st.sidebar.selectbox('sourceName',('Essen','Gelsenkirchen'))
    targetName = st.sidebar.selectbox('targetName', ('Essen', 'Gelsenkirchen'))
    totalPrice = st.sidebar.slider(' totalPrice', 0.72217,59.6,362.74041)
    totalNumberOfChanges = st.sidebar.slider('totalNumberOfChanges', 0,7)
    totalWalkingDistance = st.sidebar.slider('totalWalkingDistance', 0.0,0.5,0.96485)
    totalWaitingTime = st.sidebar.slider('totalWaitingTime', 0.0,6300.0,76630.00000)
    totalTravelTimeInSec = st.sidebar.slider('totalTravelTimeInSec', 424.0,6300.0,89987.0)
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
input_df = user_input_features()

# Combines user input features with entire routes dataset

routes_raw = pd.read_csv('combined_csv_2dim.csv')
routes = routes_raw.drop(columns=['finiteAutomaton'])
df = pd.concat([input_df,routes],axis=0)

# Encoding of ordinal features
encode = ['objective', 'consideredPreferences', 'sourceName', 'targetName','finalSolutionUsedLabels']
for col in encode:
    dummy = pd.get_dummies(df[col], prefix=col)
    df = pd.concat([df,dummy], axis=1)
    del df[col]
df = df[:1] # Selects only the first row (the user input data)

# Displays the user input features
st.subheader('User Input features')


st.write(df)

if st.sidebar.button('Done'):

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


