import pickle
import re

import pandas as pd
import pydeck as pdk
from sklearn.preprocessing import OrdinalEncoder

from dashboardCalculations import *
from multipage import *

# Config and setup
st.set_page_config(layout="wide", page_title="Transport Recommendation Dashboard", menu_items={
    'Get Help': 'https://plotly.com/python/parallel-coordinates-plot/',
    'About': "# App for the route recommendation. \n"
             "Version 1.0"
})

pd.options.display.max_colwidth = 300

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
routes_raw = pd.read_csv('./data.csv')
gis_data = pd.read_csv("./gis_data.csv", encoding='utf-8', delimiter=";", index_col=0)
gis_tourist_data = pd.read_csv("./gisInfo_touristInfo_final.csv", encoding='utf-8', delimiter=",", index_col=0)

# Extracting only unique and sorted lists of ODs
sources = routes_raw['sourcename'].sort_values().unique()
targets = routes_raw['targetname'].sort_values().unique()

totalprice = "Price"
totalwaitingtimeinhours = "Total Waiting Time"
totaltraveltimeinhours = "Total Travel Time"
totalwalkingdistance = "Total Walking Distance"

cities_distance = {}


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

                    st.write(" The best transport recommendation (based on your preference) is:")
                    st.write(":arrow_right: In order to reach the final destination you need to cover : __" +
                             best_recommendation_df["distance"].to_string(index=False) + "__ km.")
                    st.write(f":thumbsup: Based on the survey your preference is: __{preference}__.")
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

                    if best_recommendation_df.luggage_transportation.to_string(
                            index=False) == "unlimited carry-on and standard bags,no extra charge":
                        st.write(
                            ":handbag: The luggage policy is generous, enjoy your trip with no limitations on board of RE/RB, Deutsche Bahn- trains")
                    elif best_recommendation_df.luggage_transportation.to_string(
                            index=False) == "1 carry-on bag up to 7 kg, 1 free checked baggage up to 20 kg, additional bags per fee":
                        st.write(
                            ":handbag: The luggage policy is pretty strict, although suitcases may not be checked and weighed. However, it is recommended to follow the rules of the carrier company: an upper bound is 1 carry-on bag up to 7 kg& 1 free checked baggage up to 20 kg. Additional bags might be included per fee")
                    elif best_recommendation_df.luggage_transportation.to_string(
                            index=False) == "2 pieces of hand luggage, 2 free pieces of checked baggage up to 23 kg, additional bags per fee":
                        st.write(
                            ":handbag: The luggage policy is moderate and you can bring a lot of things with you.The suitcases may not be checked and weighed. However, it is recommended to follow the rules of the carrier company: an upper bound is 2 pieces of hand luggage, 2 free pieces of checked baggage up to 23 kg, additional bags per fee ")

                    elif best_recommendation_df.luggage_transportation.to_string(
                            index=False) == "several hand bags, 6 bags, unlimited weight":
                        st.write(
                            ":handbag: You are the host of your own baggage policy, since you are traveling by your private car. It is recommended to take into account the number of passengers in the car and the volume of the trunk to calculate the luggage that can be placed inside ")

                    elif best_recommendation_df.luggage_transportation.to_string(
                            index=False) == "1 carry-on bag up to 8kg, 1 free checked baggage up to 23 kg, additional bags per fee":
                        st.write(
                            ":handbag: The luggage policy is strict, the suitcases will be 100% checked with respect to the dimensions and weighed. It is highly recommended to follow the rules of the carrier company: an upper bound is 1 carry-on bag up to 8kg, 1 free checked baggage up to 23 kg, additional bags per fee ")

                    if best_recommendation_df.meal_option.to_string(
                            index=False) == "catering trolley, on-board catering with 2-g rule":
                        st.write(
                            ":stew: There is no need to prepare the snacks in advance, you can buy them on board. Restaurant serving options are possible in compliance with 2-g rule ")
                    elif best_recommendation_df.meal_option.to_string(
                            index=False) == "prepared own snacks, on-board purshase of low cost snacks&drinks + catering trolley, on-board catering with 2-g rule":
                        st.write(
                            ":stew: There is no need to bring the snacks with you, it would be possible to buy them in a bus. Restaurant serving options are available in compliance with 2-g rule in trains. However, your trip is combined and you may consider to buy your own edibles in advance. ")
                    elif best_recommendation_df.meal_option.to_string(
                            index=False) == "prepared cold food&drinks, no alcohol + catering trolley, on-board catering with 2-g rule":
                        st.write(
                            ":stew: You could only eat your own cold food in a bus. Catering trolley and the restaurant serving options are possible in compliance with 2-g rule in trains ")
                    elif best_recommendation_df.meal_option.to_string(
                            index=False) == "prepared own snacks, on-board purshase of low cost snacks&drinks":
                        st.write(
                            ":stew: You can either prepare your own simple snacks and drinks in advance or purchase them on board the bus ")

                    elif best_recommendation_df.meal_option.to_string(
                            index=False) == "prepared own snacks, buying at gas stations":
                        st.write(
                            ":stew: Driving your own car, consider the possibility of having a meal prepared in advance or stop at a gas station to satisfy your hunger ")



                    elif best_recommendation_df.meal_option.to_string(
                            index=False) == "catering trolley, on-board catering with 2-g rule+ prepared own snacks, on-board purshase of low cost snacks&drinks+ prepared cold food&drinks, no alcohol":
                        st.write(
                            ":stew: Your trip incudes 3 different transports, where you can either buy food on board or bring your own food in advance. To get service in a restaurant , you must follow the 2-g rule ")

                    elif best_recommendation_df.meal_option.to_string(
                            index=False) == "prepared cold food&drinks, no alcohol+ prepared own snacks, on-board purshase of low cost snacks&drinks":
                        st.write(
                            ":stew: Not all buses are equipped with the option of buying food, it is better to take care of your own nutritious cold snacks and beverages in advance ")

                    elif best_recommendation_df.meal_option.to_string(
                            index=False) == "prepared cold food&drinks, no alcohol":
                        st.write(
                            ":stew: It is necessary to bring food with you, buying on board would be impossible, just like drinking alcohol ")

                    elif best_recommendation_df.meal_option.to_string(
                            index=False) == "prepared own snacks, on-board purshase of low cost snacks&drinks+ up to 30 min- chocolate, up to 60 min - free water, 60+ min snacks, beverages,cold vegetarian dish, alcohol is possible+ catering trolley, on-board catering with 2-g rule":
                        st.write(
                            ":stew: Your trip involves an airplane, where meals are already included and a train where, according to the 2-g rule, you can get service in a restaurant. If you want to eat more on the bus, you can buy light snacks on board ")

                    elif best_recommendation_df.meal_option.to_string(
                            index=False) == "prepared own snacks, on-board purshase of low cost snacks&drinks+ up to 30 min- chocolate, up to 60 min - free water, 60+ min snacks, beverages,cold vegetarian dish, alcohol is possible":
                        st.write(
                            ":stew: Your trip involves an airplane where meals are already included. If you want to eat more on the bus, you can buy light snacks on board or prepare the cold dishes & drinks in advance ")

                    if (best_recommendation_df.possible_expences == 4).bool():
                        st.write(
                            ":money_with_wings: The cost of living is relatively modest, enjoy your journey without high prices for goods and services")
                    elif (best_recommendation_df.possible_expences == 3).bool():
                        st.write(
                            ":money_with_wings: The cost of living is moderate, prices for goods and services are in the middle range. Most likely you will not find increased prices for goods and services ")
                    elif (best_recommendation_df.possible_expences == 2).bool():
                        st.write(
                            ":money_with_wings: Salaries in this city are quite high, which may directly indicate increased prices for goods and services, be prepared that the expenses may be significant ")
                    elif (best_recommendation_df.possible_expences == 1).bool():
                        st.write(
                            ":money_with_wings: Be prepared to spend quite a lot of money in the town of your choice, prices for goods and services will be above average, taking into account the cost of living and average net salaries of city residents ")

                    # Notification about the Filters page
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

                        show_graph_interaction_instructions()

                        # Drawing the chart
                        comparison_best_additional_fig = draw_parallel_coord(comparison_best_additional)

                        st.plotly_chart(comparison_best_additional_fig, use_container_width=True)

                else:
                    notify_no_recommendation()

                # change_page(1)

        else:
            notify_different_source_origin()


# Recommendation page
def app2(prev_vars):  # Second page
    st.write("# Transport Recommendation Dashboard")

    st.write("#### Configure filters and press the button to get the recommendations")

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

    filter_str = ""

    st.session_state.counter = 0

    with col1:
        safest_route = st.checkbox("Safest Route", )
        special_needs = st.checkbox("Special Needs", )
        delay = st.checkbox("Lowest Chance of Trip Delay")

    with col2:

        multimodality = st.checkbox("Without Transport Change", )
        mood_upgrade = st.checkbox("Improved Mood", )

    stress_level = st.multiselect("Stress level", ["low", "moderate", "high"], ["low", "moderate", "high"])

    chosenODs = routes_raw.loc[
        (routes_raw["sourcename"] == sourceName) & (routes_raw.targetname == targetName)
        ]

    chosenODs_filtered = chosenODs

    filters = [totalTravelTimeInHours, totalPrice, totalWalkingDistance, totalWaitingTime, caloriesBurnt]

    # Array for storing dictionaries of feature_name and the corresponding value of the indicator
    array_checkbox_feature_indicator = []

    # Filter by price

    if not filter_str == "":
        filter_str = filter_str + f"and Price >= {totalPrice[0]} and Price <= {totalPrice[1]}"
    else:
        filter_str = filter_str + f"Price >= {totalPrice[0]} and Price <= {totalPrice[1]}"
    # Filter by total walking distance

    if not filter_str == "":
        filter_str = filter_str + f"and `Total Walking Distance` >= {totalWalkingDistance[0]} and `Total Walking Distance` <= {totalWalkingDistance[1]}"
    else:
        filter_str = filter_str + f"`Total Walking Distance` >= {totalWalkingDistance[0]} and `Total Walking Distance` <= {totalWalkingDistance[1]}"
    # Filter by total waiting time

    if not filter_str == "":
        filter_str = filter_str + f"and `Total Waiting Time` >= {totalWaitingTime[0]} and `Total Waiting Time` <= {totalWaitingTime[1]}"
    else:
        filter_str = filter_str + f"`Total Waiting Time` >= {totalWaitingTime[0]} and `Total Waiting Time` <= {totalWaitingTime[1]}"

    # Filter by total travel time

    if not filter_str == "":
        filter_str = filter_str + f"and `Total Travel Time` >= {totalTravelTimeInHours[0]} and `Total Travel Time` <= {totalTravelTimeInHours[1]}"
    else:
        filter_str = filter_str + f"`Total Travel Time` >= {totalTravelTimeInHours[0]} and `Total Travel Time` <= {totalTravelTimeInHours[1]}"

    # Filter by calories burnt

    if not filter_str == "":
        filter_str = filter_str + f"and caloriesBurnt_avg >= {caloriesBurnt[0]} and caloriesBurnt_avg <= {caloriesBurnt[1]}"
    else:
        filter_str = filter_str + f"caloriesBurnt_avg >= {caloriesBurnt[0]} and caloriesBurnt_avg <= {caloriesBurnt[1]}"

    st.session_state.filter_str = filter_str

    increase_indicator = 15

    # Filter by the multimodality
    if multimodality:

        df_before_mult_filt = len(chosenODs.query(filter_str).index)

        if not filter_str == "":
            filter_str = filter_str + "and multimodality == 0"
        else:
            filter_str = filter_str + "multimodality == 0"

        df_after_mult_filt = len(chosenODs.query(filter_str).index)

        array_checkbox_feature_indicator.append(
            indicator_calculation_checkboxes(df_after_mult_filt, df_before_mult_filt,
                                             increase_indicator, "Without Transport Change"))

    # Filter by the safest route
    if safest_route:

        df_before_safe_filt = len(chosenODs.query(filter_str).index)

        if not filter_str == "":
            filter_str = filter_str + "and safety_boost == safety_boost.max()"

        else:
            filter_str = filter_str + "safety_boost == safety_boost.max()"

        df_after_safe_filt = len(chosenODs.query(filter_str).index)

        array_checkbox_feature_indicator.append(
            indicator_calculation_checkboxes(df_after_safe_filt, df_before_safe_filt,
                                             increase_indicator, "Safest Route"))

    # Filter by the special needs
    if special_needs:

        df_before_special_needs_filt = len(chosenODs.query(st.session_state.filter_str).index)

        if not filter_str == "":
            filter_str = filter_str + "and totalwalkingdistance == totalwalkingdistance.min()"
        else:
            filter_str = filter_str + "totalwalkingdistance == totalwalkingdistance.min()"

        df_after_special_needs_filt = len(chosenODs.query(st.session_state.filter_str).index)

        array_checkbox_feature_indicator.append(indicator_calculation_checkboxes(df_after_special_needs_filt,
                                                                                 df_before_special_needs_filt,
                                                                                 increase_indicator,
                                                                                 "Special Needs"))

    # Filter by the stress level

    if stress_level:

        df_before_stress_level_filt = len(chosenODs.query(filter_str).index)

        if not filter_str == "":
            filter_str = filter_str + f"and stresslevel.isin({stress_level})"
        else:
            filter_str = filter_str + f"stresslevel.isin({stress_level})"

        df_after_stress_level_filt = len(chosenODs.query(filter_str).index)

        array_checkbox_feature_indicator.append(indicator_calculation_checkboxes(df_after_stress_level_filt,
                                                                                 df_before_stress_level_filt,
                                                                                 increase_indicator, "Stress Level"))

    # Filter by the mood upgrade

    if mood_upgrade:

        df_before_mood_upgrade_filt = len(chosenODs.query(filter_str).index)

        if not filter_str == "":
            filter_str = filter_str + "and mood_upgrade == \"achieved\")"
        else:
            filter_str = filter_str + "mood_upgrade == \"achieved\")"

        df_after_mood_upgrade_filt = len(chosenODs.query(filter_str).index)

        array_checkbox_feature_indicator.append(indicator_calculation_checkboxes(df_after_mood_upgrade_filt,
                                                                                 df_before_mood_upgrade_filt,
                                                                                 increase_indicator,
                                                                                 "Mood Upgrade"))

    # Filter by the delay
    if delay:

        df_before_delay_filt = len(chosenODs.query(filter_str).index)

        if not filter_str == "":
            filter_str = filter_str + "and delay_probability == delay_probability.min()"
        else:
            filter_str = filter_str + "delay_probability == delay_probability.min()"

        df_after_delay_filt = len(chosenODs.query(filter_str).index)

        array_checkbox_feature_indicator.append(
            indicator_calculation_checkboxes(df_after_delay_filt, df_before_delay_filt,
                                             increase_indicator, "Lowest Chance of Trip Delay"))

    if sourceName != targetName:

        if st.button("Recommend"):

            # Applying filtering
            if not filter_str == "":
                chosenODs_filtered = chosenODs.query(filter_str)

            chosenODs_filtered.reset_index(drop=True, inplace=True)
            chosenODs_filtered = assign_ids(chosenODs_filtered)

            if chosenODs_filtered.empty:
                notify_no_recommendation()

            else:

                st.subheader("Your route recommendations")

                chosenODs_filtered.drop(["distance"], axis=1, inplace=True)

                chosenODs_filtered.drop_duplicates(inplace=True)

                st.write(chosenODs_filtered)

                show_graph_interaction_instructions()

                fig = draw_parallel_coord(chosenODs_filtered)

                st.plotly_chart(fig, use_container_width=True)

                # Checking the amount of lines on the graph. If a lot, then show an advice
                friendly_amount_lines = 7
                check_amount_lines(chosenODs_filtered, friendly_amount_lines)

            # Show filter indicators section
            if len(chosenODs_filtered.index) < len(chosenODs.index):
                st.subheader("Filter indicators")

                indicator_calculation_sliders(increase_indicator, filters, chosenODs, chosenODs_filtered)

                # Check each object in dictionary and if it has specific value of an indicator, show the name and
                # value of the indicator
                for el in array_checkbox_feature_indicator:

                    if el["number_indicators"] == 1:
                        st.write(f"{el['feature_name']} :arrow_up:")
                    elif el["number_indicators"] == 2:
                        st.write(f"{el['feature_name']} :arrow_up: :arrow_up:")
                    elif el["number_indicators"] == 3:
                        st.write(f"{el['feature_name']} :arrow_up: :arrow_up: :arrow_up:")

                st.info(
                    "- :arrow_up: -- by adjusting this feature, additional recommendations will appear \n"

                    # "- :arrow_up: -- by adjusting this feature, a few of additional recommendations can appear \n"
                    # "- :arrow_up: :arrow_up: -- by adjusting this feature, a dozen of additional recommendations can appear \n"
                    # "- :arrow_up: :arrow_up: :arrow_up: -- by adjusting this feature, a lot of additional recommendations can appear \n"
                )
    else:
        notify_different_source_origin()


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
            'targetname': targetName
        }
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


# Map page
def app4(prev_vars):
    st.title("GIS Routing")
    # Create a text element and let the reader know the data is loading.

    # very basic map
    st.subheader('All cities in travel system:')
    # data_load_state = st.text('Loading GIS data...')
    st.map(gis_data)

    # list of origin and destination cities
    st.subheader('Find your route:')
    origins = gis_tourist_data['origin'].sort_values().unique().tolist()
    sourceName = st.selectbox('Origin', origins)
    destinations = gis_tourist_data['destination'].sort_values().unique().tolist()
    targetName = st.selectbox('Destination', destinations)
    st.info("You selected: {} - {}".format(sourceName, targetName))

    if sourceName != targetName:
        OD_pair = str(sourceName + "-" + targetName)
        # get route info
        chosenOD = gis_tourist_data.loc[
            (gis_tourist_data['routes'] == OD_pair)]  # & (gis_tourist_data['destination'] == targetName)]

        # fancier map
        chosenPath = chosenOD.path.item()

        origin_gis = chosenOD.origin_gis.values[0]
        destination_gis = chosenOD.destination_gis.values[0]
        orig_lon = float(origin_gis.split(", ")[0].replace('[', ''))
        orig_lat = float(origin_gis.split(", ")[1].replace(']', ''))
        dest_lon = float(destination_gis.split(", ")[0].replace('[', ''))
        dest_lat = float(destination_gis.split(", ")[1].replace(']', ''))

        def get_middle_gis(oLon, oLat, dLon, dLat):
            lon = (oLon + dLon) / 2
            lat = (oLat + dLat) / 2

            return lon, lat

        middle_lon, middle_lat = get_middle_gis(orig_lon, orig_lat, dest_lon, dest_lat)

        origin_info = chosenOD.origin_info.values[0]
        destination_info = chosenOD.destination_info.values[0]

        origin_name = chosenOD.origin.values[0]
        destination_name = chosenOD.destination.values[0]

        st.write("Would you like to get some information on your destination city?")
        agree = st.checkbox("Yes, please")
        if agree:
            st.write("Follow this link:", destination_info)

        middle_ger_lon = 51.163361
        middle_ger_lat = 10.447683
        view = pdk.ViewState(
            latitude=middle_lat,
            longitude=middle_lon,
            zoom=5.5)

        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/streets-v11',
            initial_view_state=view,
            layers=[
                pdk.Layer(
                    'PathLayer',
                    data=chosenOD,
                    pickable=True,
                    get_color='[200, 30, 0, 160]',
                    width_scale=20,
                    width_min_pixels=4,
                    get_path=chosenPath,
                    get_width=5),
                pdk.Layer(
                    'ScatterplotLayer',
                    chosenOD,
                    pickable=True,
                    opacity=0.8,
                    stroked=True,
                    filled=True,
                    radius_scale=6,
                    radius_min_pixels=5,
                    line_width_min_pixels=1,
                    get_position=origin_gis,
                    get_radius=60,
                    get_fill_color=[64, 64, 64, 160],
                    get_line_color=[0, 0, 0],
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    chosenOD,
                    pickable=True,
                    opacity=0.8,
                    stroked=True,
                    filled=True,
                    radius_scale=6,
                    radius_min_pixels=5,
                    line_width_min_pixels=1,
                    get_position=destination_gis,
                    get_radius=60,
                    get_fill_color=[200, 30, 0, 160],
                    get_line_color=[0, 0, 0],
                ),
                pdk.Layer(
                    "TextLayer",
                    chosenOD,
                    pickable=True,
                    get_position=origin_gis,
                    get_text=origin_name,
                    get_size=16,
                    get_color=[64, 64, 64],
                    get_angle=0
                )
            ]
        ))


app.set_initial_page(startpage)
app.add_app("Survey", app1)
app.add_app("Filters", app2)
# app.add_app("Prediction", app3)
app.add_app("Mapping", app4)
app.run()
