import pickle
import re
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

# Check the input of select boxes
# def ods_input_check(sourceName, targets):
#     for element in targets:
#         if element == sourceName:
#             return np.delete(targets, element.index(element))


st.write("#### Configure filters and press the button on the sidebar to get the recommended mode for your choice")


# Questionnaire for the traveler to preconfigure filters
form = st.empty()
with form.form("my_form"):
    st.write("What is the most important value for you in your itinerary?")
    preference = st.selectbox('Filter type', ('Price', 'Waiting Time'))
    submitted = st.form_submit_button("Submit")


    if submitted:
        form.empty()


if preference == 'Price':
        price_default = 0
        waiting_time_default = 1.0
else:
        waiting_time_default = 0.0
        price_default = 20

    # Setting up the sidebar
sourceName = st.sidebar.selectbox('Origin', sources)
targetName = st.sidebar.selectbox('Destination', targets, index=1)
totalPrice = st.sidebar.slider('Price (Euro)', 0, 59, price_default)
totalNumberOfChanges = st.sidebar.slider('Number of changes', 0, 7, 1)
totalWalkingDistance = st.sidebar.slider('Walking distance (m)', 0, 965, 200)
totalWaitingTime = st.sidebar.slider('Waiting time (h)', 0.0, 3.5, waiting_time_default, step=0.5)
totalTravelTimeInSec = st.sidebar.slider('Travel time (h)', 0, 260, 4)


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
if st.sidebar.button('Recommend'):
    form.empty()
    with st.spinner('Processing...'):


        if sourceName != targetName:

            input_df = user_input_features(sourceName, targetName, totalPrice, totalNumberOfChanges,
                                           totalWalkingDistance,
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

            st.subheader('Recommendation')

            # Extracting the mapped to the encoded values list of ODs
            ord_enc = OrdinalEncoder()
            routes_raw["finalsolutionusedlabels_code"] = ord_enc.fit_transform(routes_raw[["finalsolutionusedlabels"]])

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
            st.error('Recommendation cannot be done. Please select the destination that is different from the origin')
