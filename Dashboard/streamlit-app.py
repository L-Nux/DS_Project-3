import pickle
import re

import pandas as pd
from sklearn.preprocessing import OrdinalEncoder


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

# First page
def app1(prev_vars):

    # Questionnaire for the traveler to preconfigure filters

    with st.form("myform"):
        st.write("### Survey to provide you with the best recommendation")
        st.info("We do not store the information provided by you in this survey!")
        sourceName = st.selectbox('Origin', sources)
        targetName = st.selectbox('Destination', targets, index=1)
        # st.write("What is the most important value for you in your itinerary?")
        # preference = st.selectbox('Filter type', ('Price', 'Waiting Time'))
        travel_kids = st.selectbox('Do you travel with kids?', ('Yes', 'No'))

        chosenODs = routes_raw.loc[
            (routes_raw["sourcename"] == sourceName) & (routes_raw.targetname == targetName)
            ]

        preference = survey_pref_calc(travel_kids)


        if sourceName != targetName:

            if st.form_submit_button("Submit"):
                # Saving variables to use them on the recommendation page
                save(var_list=[survey_pref_calc(travel_kids), sourceName, targetName], name="Survey",
                     page_names=["Manual Filters"])

                best_recommendation_df = chosenODs[(chosenODs[preference] == chosenODs[preference].min())].head(1)
                st.write(f"Your preference is: {preference}.")
                st.write("The best recommendation (based on your preference) is:")
                st.write("__" + best_recommendation_df["finalsolutionusedlabels"].to_string(index=False) + "__")

                # Generating the additional recommendation
                if not best_recommendation_df.empty:
                    # User-friendly output
                    # st.write(best_recommendation_df["sourcename"].to_string(index=False))
                    additional_recommendation_df = additional_recommendation(chosenODs, preference)

                    comparison_best_additional = pd.concat([best_recommendation_df, additional_recommendation_df],
                                                           axis=0)

                    comparison_best_additional.reset_index(drop=True, inplace=True)

                    comparison_best_additional.drop(["distance", "multimodality"], axis=1, inplace=True)

                    comparison_best_additional = assign_ids(comparison_best_additional)

                    comparison_best_additional_fig = draw_parallel_coord(comparison_best_additional)

                    st.plotly_chart(comparison_best_additional_fig, use_container_width=True)

                else:
                    st.warning(
                        "Unfortunately, there is no recommendation for the chosen itinerary. Please select another one")

                #change_page(1)

        else:
            st.error(
                'Recommendation cannot be done. Please select the destination that is different from the origin')


# Recommendation page
def app2(prev_vars):  # Second page
    st.write("# Transport Recommendation App")


        # Checking if survey was filled in
        # if preference:
        #
        #
        #
        # else:
        #     return "### Please fill in the survey to get the best recommendation based on our algorithm"

    # else:
    #     st.info("Please fill in the survey to get the best recommendation.")

    # Manual filtering section
    # with st.expander('Manual filtering'):

    st.write("#### Configure filters and press the button to get the recommended mode for your choice")





    # Setting up filters based on the survey
    if prev_vars is not None:
        preference = prev_vars[0]
        sourceName = prev_vars[1]
        targetName = prev_vars[2]


        sourceName = st.selectbox('Origin', sources, sources.tolist().index(sourceName))
        targetName = st.selectbox('Destination', targets, targets.tolist().index(targetName))

        # Setting up upper limits for filters

        price_upper_limit = routes_raw["totalprice"].max()
        total_waiting_time_upper_limit = routes_raw["totalwaitingtimeinhours"].max()
        total_travel_time_upper_limit = routes_raw["totaltraveltimeinhours"].max()
        total_walking_distance_upper_limit = routes_raw["totalwalkingdistanceinm"].max()

        match preference:
            case 'totalprice':

                price_upper_limit = 1

            case 'totalwaitingtimeinhours':
                total_waiting_time_upper_limit = 0
            case 'totaltraveltimeinhours':

                total_travel_time_upper_limit = 0

            case 'totalwalkingdistanceinm':
                total_walking_distance_upper_limit = 0

        totalPrice = st.slider('Price (Euro)', 1.0, 363.0, (1.0, float(price_upper_limit)), step=0.5)

        # totalPrice_upper_value = totalPrice[1]
        # totalPrice_lower_value = totalPrice[0]
        # change_in_total_price = change_in_filter(totalPrice_upper_value, totalPrice_lower_value, totalPrice)

        totalWalkingDistance = st.slider('Walking distance (m)', 0, 965,
                                         (0, int(total_walking_distance_upper_limit)))

        totalWaitingTime = st.slider('Waiting time (h)', 0.0, 3.5,
                                     (0.0, float(total_waiting_time_upper_limit)),
                                     step=0.5)

        totalTravelTimeInHours = st.slider('Travel time (h)', 0.5, 4.5,
                                           (0.0, float(total_travel_time_upper_limit)),
                                           step=0.5)



    # Setting up filters
    else:


        sourceName = st.selectbox('Origin', sources)
        targetName = st.selectbox('Destination', targets, index=1)



        totalPrice = st.slider('Price (Euro)', 1.0, 363.0, (1.0, 363.0), step=0.5)
        totalWalkingDistance = st.slider('Walking distance (m)', 0, 965, (0, 965))
        totalWaitingTime = st.slider('Waiting time (h)', 0.0, 22.0, (0.0, 22.0), step=0.5)
        totalTravelTimeInHours = st.slider('Travel time (h)', 0.5, 24.0, (0.0, 24.0), step=0.5)


        caloriesBurnt = st.slider('Calories burnt',10,2125,(10, 2125),step=5)

        col1, col2 = st.columns(2)

    with col1:
        safest_route = st.checkbox("Safest Route")
        special_needs = st.checkbox("Special Needs")
        delay = st.checkbox("Smallest Chance of Trip Delay")

    with col2:

        multimodality = st.checkbox("Without Transport Change")
        mood_upgrade = st.checkbox("Improve Mood")

    stress_level = st.multiselect("Stress level", ["low", "moderate", "high"], ["low", "moderate", "high"])


    chosenODs = routes_raw.loc[
        (routes_raw["sourcename"] == sourceName) & (routes_raw.targetname == targetName)
        ]


    chosenODs_filtered = chosenODs
    filters = [totalTravelTimeInHours, totalPrice, totalWalkingDistance, totalWaitingTime, caloriesBurnt]


    if sourceName != targetName:
        # Filter by price
        chosenODs_filtered = chosenODs_filtered.loc[(chosenODs_filtered.totalprice >= totalPrice[0]) & (
                chosenODs_filtered.totalprice <= totalPrice[1])]
        # Filter by total walking distance
        chosenODs_filtered = chosenODs_filtered.loc[
            (chosenODs_filtered.totalwalkingdistanceinm >= totalWalkingDistance[
                0]) & (
                    chosenODs_filtered.totalwalkingdistanceinm <=
                    totalWalkingDistance[1])]
        # Filter by total waiting time

        chosenODs_filtered = chosenODs_filtered.loc[
            (chosenODs_filtered.totalwaitingtimeinhours >= totalWaitingTime[0]) & (
                chosenODs_filtered.totalwaitingtimeinhours <= totalWaitingTime[1])]

        # Filter by total travel time

        chosenODs_filtered = chosenODs_filtered.loc[
            (chosenODs_filtered.totaltraveltimeinhours >= totalTravelTimeInHours[0]) & (
                chosenODs_filtered.totaltraveltimeinhours <= totalTravelTimeInHours[1])]

        # Filter by calories burnt

        chosenODs_filtered = chosenODs_filtered.loc[
            (chosenODs_filtered.caloriesBurnt_avg >= caloriesBurnt[0]) & (
                    chosenODs_filtered.caloriesBurnt_avg <= caloriesBurnt[1])]

        # Filter by the multimodality
        if multimodality:
            chosenODs_filtered = chosenODs_filtered.loc[
                (chosenODs_filtered.multimodality == 0)]

        # Filter by the safest route

        if safest_route:
            chosenODs_filtered = chosenODs_filtered.loc[
                (chosenODs_filtered.safety_boost == chosenODs_filtered.safety_boost.max())]

        # Filter by the special needs
        if special_needs:
            chosenODs_filtered = chosenODs_filtered.loc[
                (chosenODs_filtered.totalwalkingdistanceinm == chosenODs_filtered.totalwalkingdistanceinm.min())]

        # Filter by the stress level

        if  stress_level:
            chosenODs_filtered=chosenODs_filtered[chosenODs_filtered.stresslevel.isin(stress_level)]

        # Filter by the mood upgrade

        if mood_upgrade:
            chosenODs_filtered = chosenODs_filtered[chosenODs_filtered.mood_upgrade == "achieved"]




        # Filter by the delay
        if delay:
            chosenODs_filtered=chosenODs_filtered[chosenODs_filtered.delay_probability == chosenODs_filtered.delay_probability.min()]


        chosenODs_filtered.reset_index(drop=True, inplace=True)
        chosenODs_filtered = assign_ids(chosenODs_filtered)

        if st.button("Recommend"):


            if chosenODs_filtered.empty:
                st.warning(
                    "Unfortunately, there is no recommendation for the chosen filters. Please choose different values")
            else:

                st.write(chosenODs_filtered)

            st.write(len(chosenODs.index))
            st.write(len(chosenODs_filtered.index))

        # final_solutions = chosenODs['finalsolutionusedlabels']

        # Make the transport labels look user-friendly
        # clean_recommendation = []

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

            fig = draw_parallel_coord(chosenODs_filtered)

            st.plotly_chart(fig, use_container_width=True)

            # Checking the amount of lines on the graph. If a lot, then show an advice
            friendly_amount_lines = 7
            check_amount_lines(chosenODs_filtered, friendly_amount_lines)

            show_indicators(chosenODs_filtered, chosenODs, filters)

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
    totalPrice = st.slider('Price (Euro)', 1, 363, 0)
    totalWalkingDistance = st.slider('Walking distance (m)', 0, 965, 200)
    totalWaitingTime = st.slider('Waiting time (h)', 0.0, 3.5, 0.0, step=0.5)
    totalTravelTimeInHours = st.slider('Travel time (h)', 0.5, 4.5, 3.0, step=0.5)

    # Accepting the user input
    def user_input_features(sourceName, targetName, totalPrice, totalWalkingDistance,
                            totalWaitingTime, totalTravelTimeInHours):
        data = {
            'totaltraveltimeinhours': totalTravelTimeInHours,
            'totalprice': totalPrice,
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

                input_df = user_input_features(sourceName, targetName, totalPrice,
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
app.add_app("Manual Filters", app2)
app.add_app("Prediction", app3)
app.run()
