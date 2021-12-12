import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder

routes = pd.read_csv('./data.csv')

# Ordinal feature encoding
df = routes.copy()
target = 'finalsolutionusedlabels'
encode = ['objective', 'consideredpreferences', 'sourcename', 'targetname', 'finiteautomaton']

insight = df.describe()

for col in encode:
    dummy = pd.get_dummies(df[col], prefix=col)
    df = pd.concat([df, dummy], axis=1)
    del df[col]

ord_enc = OrdinalEncoder()
df["finalsolutionusedlabels_code"] = ord_enc.fit_transform(df[["finalsolutionusedlabels"]])

# Separating X and y
X = df.drop(['finalsolutionusedlabels_code', 'finalsolutionusedlabels'], axis=1)
Y = df['finalsolutionusedlabels_code']

# Splitting the dataset
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3)

# Build random forest model
from sklearn.ensemble import RandomForestClassifier

clf = RandomForestClassifier(n_estimators=100)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

from sklearn import metrics

# Checking the accuracy of the model
print("Accuracy:", metrics.accuracy_score(y_test, y_pred))

# Saving the model
import pickle

pickle.dump(clf, open('routes_clf.pkl', 'wb'))
