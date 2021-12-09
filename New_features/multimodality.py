import pandas as pd

###NEW FEATURE: Multimodality
#binary feature [0,1] 0 --> unimodal, 1 --> multimodal

def check_multimodal(df):
    sol_labels = df['finalsolutionusedlabels'].values[0]
    label_count = sol_labels.count(", ")
    if label_count < 1:
        return 0
    else:
        return 1

###only for testing purposes###
path_source = "/home/lisnux/Desktop/UniWien/WS2122/DS_Project/data/Marina_data/"
df_3dim = pd.read_csv(path_source+"2featuresout.csv", encoding = 'utf-8')

test1 = df_3dim.sample() #type: #class pandas.core.frame.DataFrame
print(test1['finalsolutionusedlabels'])
print(check_multimodal(test1))