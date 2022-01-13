import ast
import pickle
import re

import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

from dashboardCalculations import *
from multipage import *

# Config and setup
st.set_page_config(layout="wide", page_title="Transport Recommendation Dashboard", menu_items={
    'Get Help': 'https://plotly.com/python/parallel-coordinates-plot/',
    'About': "# App for the route recommendation. \n"
             "Version 1.0"
})

# References:
# Streamlit multipage framework:
# https://github.com/YanAlmeida/streamlit-multipage-framework


start_app()  # Clears the cache when the app is started

app = MultiPage()

app.start_button = "Let's start!"
app.navbar_name = "Navigation"

app.next_page_button = "Next Page"
app.previous_page_button = "Previous Page"

# Reading the dataset
routes_raw = pd.read_csv('../data.csv')

# Extracting only unique and sorted lists of ODs
sources = routes_raw['sourcename'].sort_values().unique()
targets = routes_raw['targetname'].sort_values().unique()

totalprice = "Price"
totalwaitingtimeinhours = "Total Waiting Time"
totaltraveltimeinhours = "Total Travel Time"
totalwalkingdistance = "Total Walking Distance"


def startpage():
    st.write("# Welcome to the Itinerary Planning Dashboard :wave: ")


# First page
def app1(prev_vars):
    # Questionnaire for the traveler

    st.write("# Transport Recommendation Dashboard")

    with st.form("myform"):
        st.write("### Survey to provide you with the best recommendation")
        sourceName = st.selectbox('Origin', sources)
        targetName = st.selectbox('Destination', targets, index=1)

        st.write("####  :question: Questions")

        col1, col2 = st.columns(2)

        with col1:

            goal = st.selectbox('What goal do you have for your trip?',
                                ('Leisure', 'Adventure', 'Quality time with family',
                                 'Learn about experience/culture', 'Daily business',
                                 'Other'))
            travel_kids = st.selectbox('Do you travel with kids?', ('Yes', 'No'))
            age = st.selectbox('What is your age range?', ('16-25', '25-45', '45-65',
                                                           '>65', 'I do not want to tell',))

        with col2:

            trip_duration = st.selectbox('How many days do you plan for this trip?', ('<1', '1-3', '>3'))
            comfort_level = st.selectbox('What comfort level do you prefer?',
                                         ('Comfort does not matter much to me (better cheaper)',
                                          'I am fine to be a bit uncomfortable during the trip',
                                          'I prefer to have full comfort'))
            disability = st.selectbox('Do you have a disability that could impact your traveling experience?',
                                      ('Yes', 'No', 'I prefer not to answer'))
        st.warning("We do not store your answers on the questions!")

        chosenODs = routes_raw.loc[
            (routes_raw["sourcename"] == sourceName) & (routes_raw.targetname == targetName)
            ]

        preference = survey_pref_calc(goal, travel_kids, age, trip_duration, comfort_level, disability)

        if sourceName != targetName:

            if st.form_submit_button("Submit"):
                # Saving variables to use them on the filters page
                save(var_list=[preference, sourceName, targetName], name="Survey",
                     page_names=["Filters"])

                best_recommendation_df = chosenODs[(chosenODs[preference] == chosenODs[preference].min())].head(1)

                # Generating the additional recommendation and showing all messages
                if not best_recommendation_df.empty:

                    st.write(f":thumbsup: Based on the survey your preference is: __{preference}__.")
                    st.write(" The best transport recommendation (based on your preference) is:")
                    st.success(
                        ":minibus: __" + best_recommendation_df["finalsolutionusedlabels"].to_string(index=False).strip(
                            "[]") + "__")
                    st.write(
                        f":beginner: This choice is __{best_recommendation_df.safety_boost.to_string(index=False)}__ times safer than driving by car")

                    if best_recommendation_df.stresslevel.to_string(index=False) == "low":
                        st.write(
                            ":mask: The COVID-19 incidence rate is relatively small. But better __do the test before traveling and keep the distance__")
                    elif best_recommendation_df.stresslevel.to_string(index=False) == "moderate":
                        st.write(
                            ":mask: Travelers without vaccination who are at increased risk for severe illness from COVID-19 should __avoid nonessential travel to this destination__")
                    elif best_recommendation_df.stresslevel.to_string(index=False) == "high":
                        st.write(
                            ":mask: Travelers without vaccination should __avoid nonessential travel to this "
                            "destination__")

                    st.write(
                        f":muscle: You will burn approximately __{best_recommendation_df.caloriesBurnt_avg.to_string(index=False)}__ calories during your trip")

                    if best_recommendation_df.mood_upgrade.to_string(index=False) == "achieved":

                        st.write(
                            ":blush: The weather in your target destination is pleasant. Expect to spend your time there with the __elevated mood__")
                    elif best_recommendation_df.mood_upgrade.to_string(index=False) == "not_achieved ":
                        st.write(
                            ":worried: The weather in your target destination is not the best. It could __influence your mood in a bad way__")

                    st.write(
                        f":moneybag: You could earn __{best_recommendation_df.earnings_gross.to_string(index=False)} Euro__ working instead of traveling this amount of time")
                    st.write(
                        f":traffic_light: Probability that you will not arrive on time is __{best_recommendation_df.delay_probability.to_string(index=False)}__")
                    st.info(
                        "For more flexibility in filtering, move to the \"Filters\" page")

                    with st.expander("Additional recommendation"):
                        # Receiving the additional recommendation
                        additional_recommendation_df = additional_recommendation(chosenODs, preference)

                        # Concatenating the best and additional recommendations
                        comparison_best_additional = pd.concat([best_recommendation_df, additional_recommendation_df],
                                                               axis=0)

                        comparison_best_additional.reset_index(drop=True, inplace=True)

                        comparison_best_additional.drop(["distance"], axis=1, inplace=True)

                        comparison_best_additional.drop_duplicates(inplace=True)

                        comparison_best_additional = assign_ids(comparison_best_additional)

                        graph_interaction_instructions()

                        # Drawing the chart
                        comparison_best_additional_fig = draw_parallel_coord(comparison_best_additional)

                        st.plotly_chart(comparison_best_additional_fig, use_container_width=True)

                else:
                    st.warning(
                        "Unfortunately, there is no recommendation for the chosen itinerary :pensive: Please select another one")

                # change_page(1)

        else:
            st.error(
                'Recommendation cannot be done. Please select the destination that is different from the origin')


# Recommendation page
def app2(prev_vars):  # Second page
    st.write("# Transport Recommendation Dashboard")

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

    st.write("#### Configure filters and press the button to get the recommendations")

    # TODO: preconfigure more filters
    # Setting up filters based on the survey
    if prev_vars is not None:

        st.info("Your filters are preconfigured based on your preference calculated from your answers to the survey")

        preference = prev_vars[0]
        sourceName = prev_vars[1]
        targetName = prev_vars[2]

        sourceName = st.selectbox('Origin', sources, sources.tolist().index(sourceName))
        targetName = st.selectbox('Destination', targets, targets.tolist().index(targetName))

        # Setting up upper limits for filters

        price_upper_limit = routes_raw[totalprice].max()
        total_waiting_time_upper_limit = routes_raw[totalwaitingtimeinhours].max()
        total_travel_time_upper_limit = routes_raw[totaltraveltimeinhours].max()
        total_walking_distance_upper_limit = routes_raw[totalwalkingdistance].max()

        match preference:
            case "Price":

                price_upper_limit = 1

            case "Total Waiting Time":
                total_waiting_time_upper_limit = 0
            case "Total Travel Time":

                total_travel_time_upper_limit = 0

            case "Total Walking Distance":
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

    caloriesBurnt = st.slider('Calories burnt', 10, 2125, (10, 2125), step=5)

    col1, col2 = st.columns(2)

    with col1:
        safest_route = st.checkbox("Safest Route")
        special_needs = st.checkbox("Special Needs")
        delay = st.checkbox("Lowest Chance of Trip Delay")

    with col2:

        multimodality = st.checkbox("Without Transport Change")
        mood_upgrade = st.checkbox("Improved Mood")

    stress_level = st.multiselect("Stress level", ["low", "moderate", "high"], ["low", "moderate", "high"])

    chosenODs = routes_raw.loc[
        (routes_raw["sourcename"] == sourceName) & (routes_raw.targetname == targetName)
        ]

    chosenODs_filtered = chosenODs
    # max_safety_boost = chosenODs.safety_boost.max()
    # min_totalwalkingdistance = chosenODs[totalwalkingdistance].min()

    filters = [totalTravelTimeInHours, totalPrice, totalWalkingDistance, totalWaitingTime, caloriesBurnt]

    if sourceName != targetName:

        if st.button("Recommend"):


            # Filter by price

            chosenODs_filtered = chosenODs_filtered.loc[(chosenODs_filtered[totalprice] >= totalPrice[0]) & (
                    chosenODs_filtered[totalprice] <= totalPrice[1])]
            # Filter by total walking distance
            chosenODs_filtered = chosenODs_filtered.loc[
                (chosenODs_filtered[totalwalkingdistance] >= totalWalkingDistance[
                    0]) & (
                        chosenODs_filtered[totalwalkingdistance] <=
                        totalWalkingDistance[1])]
            # Filter by total waiting time

            chosenODs_filtered = chosenODs_filtered.loc[
                (chosenODs_filtered[totalwaitingtimeinhours] >= totalWaitingTime[0]) & (
                        chosenODs_filtered[totalwaitingtimeinhours] <= totalWaitingTime[1])]

            # Filter by total travel time

            chosenODs_filtered = chosenODs_filtered.loc[
                (chosenODs_filtered[totaltraveltimeinhours] >= totalTravelTimeInHours[0]) & (
                        chosenODs_filtered[totaltraveltimeinhours] <= totalTravelTimeInHours[1])]

            # Filter by calories burnt

            chosenODs_filtered = chosenODs_filtered.loc[
                (chosenODs_filtered.caloriesBurnt_avg >= caloriesBurnt[0]) & (
                        chosenODs_filtered.caloriesBurnt_avg <= caloriesBurnt[1])]



            increase_indicator = 5


            # Array for storing dictionaries of feature_name and the corresponding value of the indicator
            array_checkbox_feature_indicator = []



            number_indicators = 0
            feature_name= ""

            # Filter by the multimodality
            if multimodality:
                chosenODs_filtered = chosenODs_filtered.loc[
                    (chosenODs_filtered.multimodality == 0)]
                feature_name = "Without Transport Change"

                # Check if the initial df bigger than filtered df and to what extent. Then assign value for an indicator
                if (len(chosenODs.index) - len(chosenODs.loc[
                            (chosenODs.multimodality == 0)].index)) >= increase_indicator and (
                        len(chosenODs.index) - len(chosenODs.loc[
                                                       (chosenODs.multimodality == 0)].index)) < increase_indicator * 2:
                    number_indicators = 1

                elif (len(chosenODs.index) - len(chosenODs.loc[
                            (chosenODs.multimodality == 0)].index)) >= increase_indicator * 2 and (
                        (len(chosenODs.index) - len(chosenODs.loc[
                            (chosenODs.multimodality == 0)].index))) < increase_indicator * 3:

                    number_indicators = 2

                elif (len(chosenODs.index) - len(chosenODs.loc[
                            (chosenODs.multimodality == 0)].index)) >= increase_indicator * 3:
                    number_indicators = 3

                array_checkbox_feature_indicator.append({"feature_name":feature_name, "number_indicators":number_indicators})
                number_indicators = 0
            # Filter by the safest route

            if safest_route:
                chosenODs_filtered = chosenODs_filtered.loc[
                    (chosenODs_filtered.safety_boost == chosenODs_filtered.safety_boost.max())]
                feature_name = "Safest Route"


                if (len(chosenODs.index) - len(chosenODs.loc[
                    (chosenODs.safety_boost == chosenODs.safety_boost.max())].index)) >= increase_indicator and (
                        len(chosenODs.index) - len(chosenODs.loc[
                    (chosenODs.safety_boost == chosenODs.safety_boost.max())].index)) < increase_indicator * 2:
                    number_indicators = 1

                elif (len(chosenODs.index) - len(chosenODs.loc[
                    (chosenODs.safety_boost == chosenODs.safety_boost.max())].index)) >= increase_indicator * 2 and (
                        (len(chosenODs.index) - len(chosenODs.loc[
                    (chosenODs.safety_boost == chosenODs.safety_boost.max())].index))) < increase_indicator * 3:

                    number_indicators = 2

                elif (len(chosenODs.index) - len(chosenODs.loc[
                    (chosenODs.safety_boost == chosenODs.safety_boost.max())].index)) >= increase_indicator * 3:
                    number_indicators = 3

                array_checkbox_feature_indicator.append({"feature_name":feature_name, "number_indicators":number_indicators})
                number_indicators = 0
            # Filter by the special needs
            if special_needs:
                chosenODs_filtered = chosenODs_filtered.loc[
                    (chosenODs_filtered[totalwalkingdistance] == chosenODs_filtered[
                        totalwalkingdistance].min())]

                feature_name = "Special Needs"
                if (len(chosenODs.index) - len(chosenODs.loc[
                    (chosenODs[totalwalkingdistance] == chosenODs[
                        totalwalkingdistance].min())].index)) >= increase_indicator and (
                        len(chosenODs.index) - len(chosenODs.loc[
                    (chosenODs[totalwalkingdistance] == chosenODs[
                        totalwalkingdistance].min())].index)) < increase_indicator * 2:
                    number_indicators = 1

                elif (len(chosenODs.index) - len(chosenODs.loc[
                    (chosenODs[totalwalkingdistance] == chosenODs[
                        totalwalkingdistance].min())].index)) >= increase_indicator * 2 and (
                        (len(chosenODs.index) - len(chosenODs.loc[
                    (chosenODs[totalwalkingdistance] == chosenODs[
                        totalwalkingdistance].min())].index))) < increase_indicator * 3:

                    number_indicators = 2

                elif (len(chosenODs.index) - len(chosenODs.loc[
                    (chosenODs[totalwalkingdistance] == chosenODs[
                        totalwalkingdistance].min())].index)) >= increase_indicator * 3:
                    number_indicators = 3

                array_checkbox_feature_indicator.append(
                    {"feature_name": feature_name, "number_indicators": number_indicators})

                number_indicators = 0

            # Filter by the stress level

            if stress_level:
                chosenODs_filtered = chosenODs_filtered[chosenODs_filtered.stresslevel.isin(stress_level)]


                feature_name = "Stress Level"
                if (len(chosenODs.index) - len(chosenODs[chosenODs.stresslevel.isin(stress_level)].index)) >= increase_indicator and (
                        len(chosenODs.index) - len(chosenODs[chosenODs.stresslevel.isin(stress_level)].index)) < increase_indicator * 2:
                    number_indicators = 1

                elif (len(chosenODs.index) - len(chosenODs[chosenODs.stresslevel.isin(stress_level)].index)) >= increase_indicator * 2 and (
                        (len(chosenODs.index) - len(chosenODs[chosenODs.stresslevel.isin(stress_level)].index))) < increase_indicator * 3:

                    number_indicators = 2

                elif (len(chosenODs.index) - len(chosenODs[chosenODs.stresslevel.isin(stress_level)].index)) >= increase_indicator * 3:
                    number_indicators = 3

                array_checkbox_feature_indicator.append(
                        {"feature_name": feature_name, "number_indicators": number_indicators})

            # Filter by the mood upgrade

            if mood_upgrade:
                chosenODs_filtered = chosenODs_filtered[chosenODs_filtered.mood_upgrade == "achieved"]

                feature_name = "Mood Upgrade"
                if (len(chosenODs.index) - len(
                        chosenODs[chosenODs.mood_upgrade == "achieved"].index)) >= increase_indicator and (
                        len(chosenODs.index) - len(
                    chosenODs[chosenODs.mood_upgrade == "achieved"].index)) < increase_indicator * 2:
                    number_indicators = 1

                elif (len(chosenODs.index) - len(
                        chosenODs[chosenODs.mood_upgrade == "achieved"].index)) >= increase_indicator * 2 and (
                        (len(chosenODs.index) - len(
                            chosenODs[chosenODs.mood_upgrade == "achieved"].index))) < increase_indicator * 3:

                    number_indicators = 2

                elif (len(chosenODs.index) - len(
                        chosenODs[chosenODs.mood_upgrade == "achieved"].index)) >= increase_indicator * 3:
                    number_indicators = 3

                array_checkbox_feature_indicator.append(
                    {"feature_name": feature_name, "number_indicators": number_indicators})
                number_indicators = 0

            # Filter by the delay
            if delay:
                chosenODs_filtered = chosenODs_filtered[
                    chosenODs_filtered.delay_probability == chosenODs_filtered.delay_probability.min()]



                feature_name = "Lowest Chance of Trip Delay"
                if (len(chosenODs.index) - len(
                        chosenODs[
                            chosenODs.delay_probability == chosenODs.delay_probability.min()].index)) >= increase_indicator and (
                        len(chosenODs.index) - len(
                    chosenODs[
                        chosenODs.delay_probability == chosenODs.delay_probability.min()].index)) < increase_indicator * 2:
                    number_indicators = 1

                elif (len(chosenODs.index) - len(
                        chosenODs[
                            chosenODs.delay_probability == chosenODs.delay_probability.min()].index)) >= increase_indicator * 2 and (
                        (len(chosenODs.index) - len(
                            chosenODs[
                                chosenODs.delay_probability == chosenODs.delay_probability.min()].index))) < increase_indicator * 3:

                    number_indicators = 2

                elif (len(chosenODs.index) - len(
                        chosenODs[
                            chosenODs.delay_probability == chosenODs.delay_probability.min()].index)) >= increase_indicator * 3:
                    number_indicators = 3

                array_checkbox_feature_indicator.append(
                    {"feature_name": feature_name, "number_indicators": number_indicators})

                number_indicators = 0



            chosenODs_filtered.reset_index(drop=True, inplace=True)
            chosenODs_filtered = assign_ids(chosenODs_filtered)

            if chosenODs_filtered.empty:
                st.warning(
                    "Unfortunately, there is no recommendation for the chosen filters. Please choose different values")

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



            st.subheader("Your route recommendations")

            chosenODs_filtered.drop(["distance"], axis=1, inplace=True)

            chosenODs_filtered.drop_duplicates(inplace=True)

            st.write(chosenODs_filtered)

            graph_interaction_instructions()

            fig = draw_parallel_coord(chosenODs_filtered)

            st.plotly_chart(fig, use_container_width=True)

            # Checking the amount of lines on the graph. If a lot, then show an advice
            friendly_amount_lines = 7
            check_amount_lines(chosenODs_filtered, friendly_amount_lines)

            st.subheader("Filter indicators")

            show_indicators_sliders(chosenODs_filtered, chosenODs, filters)

            # Check each object in dictionary and if it has specific value of an indicator, show the name and value of the indicator
            for el in array_checkbox_feature_indicator:

                if el["number_indicators"] == 1:
                    st.write(f"{el['feature_name']} :arrow_up:")
                elif el["number_indicators"] == 2:
                    st.write(f"{el['feature_name']} :arrow_up: :arrow_up:")
                elif el["number_indicators"] == 3:
                    st.write(f"{el['feature_name']} :arrow_up: :arrow_up: :arrow_up:")
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
            'Total Walking Distance': totalWalkingDistance,
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
app.add_app("Filters", app2)
# app.add_app("Prediction", app3)
app.run()
