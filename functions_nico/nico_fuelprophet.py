# This file contains all a class object which reflects the FuelProphet model

import numpy as np
import pandas as pd
from scipy.optimize import minimize

class FuelProphet():

    def __init__(self,b0,features):
        self.b = b0.copy()
        self.features = features

    def __h(self,X,b=None):
        if b == None:
            b = self.b
        return X.dot(b)

    def predict(self,X,num_predictions):

        predictions = []
        X_pred = X.copy()

        for iter in range(num_predictions):
            X_short = X_pred[self.features]
            new_value = self.__h(X_short)
            predictions.append(float(new_value))
            X_pred = np.append(X_pred,new_value)

        return np.array(predictions)
    
    def normalize(self):
        self.b = self.b/np.sum(self.b)

    def  cal_cost(self, b, X, y):

        n = len(y)
        
        predictions = self.predict(X,n)
        cost = 1/(n) * np.sum(np.abs(predictions-y))
        return cost
    
    def fit(self,X,y):
        res = minimize(lambda b: self.cal_cost(b, X, y), self.b)
        self.b = res.x

        


