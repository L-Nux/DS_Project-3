import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
from sklearn.preprocessing import LabelEncoder

from Dashboard.ANN.func_nn import *

"""
References: 
1. The Complete Guide to Neural Network multi-class Classification from scratch
https://towardsdatascience.com/the-complete-guide-to-neural-networks-multinomial-classification-4fe88bde7839
https://github.com/shaunenslin/machinelearning/tree/master/python/neural%20networks
"""


# Load the data

df = pd.read_csv("./data.csv")
df.info()

# Encode the data

columns = ["finiteautomaton", "consideredpreferences", "sourcename", "targetname"]
for feature in columns:
    le = LabelEncoder()
    df[feature] = le.fit_transform(df[feature])
df = df.drop(["objective"], axis=1)

# Encode Y
y_le = LabelEncoder()
df["finalsolutionusedlabels"] = y_le.fit_transform(df["finalsolutionusedlabels"])

# Extract Y column from the dataframe
Y = df["finalsolutionusedlabels"]
df = df.drop(["finalsolutionusedlabels"], axis=1)

# Get X/Y into arrays

X = df.to_numpy()  # np.matrix(df.to_numpy())
y = Y.to_numpy().transpose()  # np.matrix(Y.to_numpy()).transpose()

m, n = X.shape

# Normalise X

mu = X.mean(0)
sigma = X.std(0)  # standard deviation: max(x)-min(x)
xn = (X - mu) / sigma

# A column of ones to X for easier matrix manipulation of our hypothesis and cost function
xo = np.hstack((np.ones((m, 1)), xn))

# Neural network setup
input_layer_size = n  # Dimension of features
hidden_layer_size = input_layer_size * 3  # of units in hidden layer
output_layer_size = len(y_le.classes_)  # number of labels


# Initialise weights

def initializeWeights(L_in, L_out):
    epsilon_init = 0.12
    W = np.random.rand(L_out, 1 + L_in) * 2 * epsilon_init - epsilon_init
    return W


initial_Theta1 = initializeWeights(input_layer_size, hidden_layer_size)
initial_Theta2 = initializeWeights(hidden_layer_size, output_layer_size)
nn_params = np.concatenate((initial_Theta1.flatten(), initial_Theta2.flatten()), axis=None)

print('Checking Backpropagation... ')
# Weight regularization parameter (we set this to 1 here).
lambda_ = 1
#  Check gradients by running checkNNGradients
checkNNGradients(lambda_)

print('Checking Cost Function (w/ Regularization) ... ')
J, g = nnCostFunction(nn_params, input_layer_size, hidden_layer_size, output_layer_size, xn, y, lambda_)

print(f'Cost at parameters (loaded from ex4weights): {J:f}')
g

print('Training Neural Network... ')

#  Change the MaxIter to a larger value to see how more training helps.
options = {'maxiter': 50, 'disp': True}

#  You should also try different values of lambda
lambda_ = 1.1;

# Create "short hand" for the cost function to be minimized
fun = lambda nn_params: nnCostFunction(nn_params, input_layer_size, hidden_layer_size, output_layer_size, xn, y, lambda_)[0]
jac = lambda nn_params: nnCostFunction(nn_params, input_layer_size, hidden_layer_size, output_layer_size, xn, y, lambda_)[1]

# Now, costFunction is a function that takes in only one argument (the neural network parameters)
from scipy import optimize as opt
res = opt.minimize(fun, nn_params, method='CG', jac=jac, options=options)
nn_params = res.x
cost = res.fun

print(res.message)

# Obtain Theta1 and Theta2 back from nn_params
Theta1 = nn_params[:hidden_layer_size * (input_layer_size + 1)].reshape((hidden_layer_size, input_layer_size + 1))
Theta2 = nn_params[hidden_layer_size * (input_layer_size + 1):].reshape((output_layer_size, hidden_layer_size + 1))

print(cost)

pred = predict(Theta1, Theta2, X)

print(f'Training Set Accuracy: {(pred == y).mean() * 100:f}')