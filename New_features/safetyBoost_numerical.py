import pandas as pd
pd.set_option('max_columns', None)

###NEW FEATURE: Safety Boost
#approximates the increased safeness of the chosen itinerary in comparison to travelling by automobile
#Risk evaluation according to reference values from the German Federal Statistical Office

def safety_calculation(df):
    sol_labels = df['finalsolutionusedlabels'].values[0]
    #split solution labely string into list of single transport mode labels
    labels = sol_labels.strip("[|]").split(", ")
    label_count = len(labels)
    risk_automobile = 860
    risk_solution = 0
    if "flixbus" in labels:
        risk_solution += 64.9
    if "db_fv" in labels:
        risk_solution += 79.8
    if "flight" in labels:
        risk_solution += 57.2
    if "blablacar" in labels:
        risk_solution += 860
    if "car" in labels:
        risk_solution += 860

    risk_solution_avg = risk_solution/label_count
    #divide avg_risk by maximum risk (=automobile) in [%]
    gained_safety = risk_solution_avg/risk_automobile
    #calculate the multiple factor of safety in comparison to risk with automobile
    safety_factor = round(1/gained_safety)

    """ #output for dashboard 
    if safety_factor > 1:
        return "Your travel solution is {} times safer than driving by automobile".format(safety_factor)
    else:
        return "Your travel solution is as safe as driving by automobile"
    """
    return safety_factor

###only for testing purposes###
path_source = "/home/lisnux/Desktop/UniWien/WS2122/DS_Project/data/Marina_data/"
df_3dim = pd.read_csv(path_source+"2featuresout.csv", encoding = 'utf-8')

test1 = df_3dim.sample() #type: #class pandas.core.frame.DataFrame
print(test1)
print(safety_calculation(test1))