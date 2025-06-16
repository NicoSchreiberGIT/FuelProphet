# This file contains all a class object which reflects the FuelProphet model

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from statsmodels.tsa.stattools import pacf

class FuelProphet():

    def __init__(self,b0=None,features=None):
        if b0 is None:
            self.b = np.array([0.15,0.08,0.06,0.04,0.02,0.55,0.1])
        else:
            if type(b0) == np.ndarray:
                self.b = b0.copy()
            else:
                self.b = np.array(b0.copy())
    
        if features is None:
            self.features = [-1,-2,-3,-4,-5,-288,-(7*288)]
        else:
            self.features = features.copy()

        self.ds = "datetime"
        self.y  = "e5"

    def __h(self,X,b=None):
        if b is None:
            b = self.b

        return X.dot(b)

    def predict(self,X,num_predictions,b=None):

        if b is None:
            b = self.b

        time_interval = X[self.ds].iloc[1] - X[self.ds].iloc[0] # Time intervals of the data (usually 5 minutes)

        predictions = pd.DataFrame(columns=[self.ds,self.y])
        X_pred = np.array(X.copy()[self.y]) # Take only prices

        for iter in range(num_predictions):
            X_short = X_pred[self.features]
            new_value = self.__h(X_short,b=b)
            X_pred = np.append(X_pred,new_value)
            predictions = pd.concat([predictions,(pd.DataFrame([[X[self.ds].iloc[-1]+time_interval*iter,float(new_value)]], columns=[self.ds,self.y]))],ignore_index=True)

        return predictions
    
    def normalize(self):
        self.b = self.b/np.sum(self.b)

    def  cal_cost(self, b, X, y):

        n = len(y)
        
        predictions = np.array(self.predict(X,n,b=b)[self.y])
        #cost = 1/(n) * np.sum(np.abs(predictions-np.array(y[self.y])))      # MAE
        cost = 1/(2*n) * np.sum(np.square(predictions-np.array(y[self.y]))) # MSE         
        return cost
    
    def fit_minimize(self,X,y):
        bounds = [(0, 1)] * len(self.b)
        res = minimize(lambda b: self.cal_cost(b, X, y), self.b, method='L-BFGS-B', bounds=bounds, options={'maxiter': 50})
        self.b = res.x

    def fit_pacf(self,X,lags=900,threshold=0.2):
        pacf_vals = pacf(np.array(X[self.y]), nlags=lags)
        pacf_vals = pacf_vals[1:]
        lags = range(0, len(pacf_vals))

        self.features = np.negative(np.array(lags)[abs(pacf_vals) > threshold])
        self.features[self.features == 0] = -1
        self.b        = pacf_vals[self.features]
        


