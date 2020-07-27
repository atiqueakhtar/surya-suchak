# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 17:57:02 2020

@author: Atique Akhtar
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from sklearn import neighbors
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn import feature_selection
import pickle

weather_df=pd.read_csv("pavagada_nasa_dataset.csv")
weather_df.info()
weather_desc=pd.DataFrame(weather_df.describe())

weather_df['GENERATED_ENERGY'] = weather_df.apply(lambda row: row.ALLSKY_SFC_LW_DWN*1.6*15.6*0.75 , axis = 1) 

weather_df.columns
df=weather_df[['PRECTOT', 'QV2M', 'RH2M', 'PS', 'TS','T2MDEW', 'T2MWET', 'T2M_MAX', 
               'T2M_MIN', 'T2M', 'WS10M', 'WS50M','WS10M_MAX', 'WS50M_MAX', 'WS50M_MIN', 
               'WS10M_MIN', 'GENERATED_ENERGY']]
df_corr=pd.DataFrame(df.corr())

################
# CALCULATING ANOVA F-VALUE OF THE TRAINING SAMPLE :
Xtrain_f,Xtest_f,Ytrain_f,Ytest_f=train_test_split(df.drop('GENERATED_ENERGY', axis=1),df['GENERATED_ENERGY'], test_size=0.3, random_state=100)   
fvalue,probability=feature_selection.f_classif(Xtrain_f,Ytrain_f)
ser1=pd.Series(fvalue)
ser1.index=Xtrain_f.columns
ser1.sort_values(ascending=False).plot.bar()
ser1.sort_values(ascending=False,inplace=True)

################
# GENERATING CORRELATION HEATMAP PF ALL THE FEATURES :
f, ax = plt.subplots(figsize=(10, 6))
corr = Xtrain_f.corr()
hm = sns.heatmap(round(corr,2), annot=True, ax=ax, cmap="coolwarm",fmt='.2f',linewidths=.05)
f.subplots_adjust(top=0.93)
t= f.suptitle('Wheather Attributes Correlation Heatmap', fontsize=14)

#######################
# SELECTING FEATURES ON THE BASIS OF F-VALUE AND RESPECTIVE CORRELATIONS WITH OTHER FEATURES :
X=df[['PRECTOT', 'QV2M', 'PS', 'T2M_MIN', 'T2M','WS10M_MAX']]
y=df['GENERATED_ENERGY']
X_corr=pd.DataFrame(X.corr())

Xtrain,Xtest,ytrain,ytest=train_test_split(X, y, test_size=0.3, random_state=100)

########################

# LINEAR REGRESSION MODEL
lm=LinearRegression()
lm.fit(Xtrain,ytrain)

print(lm.intercept_)
print(lm.coef_)
X.columns
cdf=pd.DataFrame(lm.coef_,Xtrain.columns,columns=['coeff'])
predictions = lm.predict(Xtest)

plt.scatter(ytest,predictions)
sns.distplot((ytest-predictions)) # if normally distributed then the model is correct choice

metrics.mean_absolute_error(ytest,predictions)
metrics.mean_squared_error(ytest,predictions)
np.sqrt(metrics.mean_squared_error(ytest,predictions))



# KNN MODEL
scaler=StandardScaler()
scaler.fit(X)
scaled_features=scaler.transform(X)
X_feat=pd.DataFrame(scaled_features,columns=X.columns)

Xtrain,Xtest,ytrain,ytest=train_test_split(X_feat, y, test_size=0.3, random_state=0)

rmse_val = [] #to store rmse values for different k
for K in range(40):
    K = K+1
    model = KNeighborsRegressor(n_neighbors = K)

    model.fit(Xtrain, ytrain)  #fit the model
    pred=model.predict(Xtest) #make prediction on test set
    error = np.sqrt(metrics.mean_squared_error(ytest,pred)) #calculate rmse
    rmse_val.append(error) #store rmse values
    print('RMSE value for k= ' , K , 'is:', error)

#plotting the rmse values against k values
curve = pd.DataFrame(rmse_val) #elbow curve 
curve.plot()

knn_model = KNeighborsRegressor(n_neighbors = 25)
knn_model.fit(Xtrain, ytrain)  #fit the model
pred=knn_model.predict(Xtest) #make prediction on test set
np.sqrt(metrics.mean_squared_error(ytest,pred)) #calculate rmse



# RANDOM FOREST MODEL
rf_model=RandomForestRegressor(n_estimators=300)
rf_model.fit(Xtrain,ytrain)
pred_rf=rf_model.predict(Xtest)

plt.scatter(ytest,pred_rf)
sns.distplot((ytest-pred_rf))

metrics.mean_absolute_error(ytest,pred_rf)
metrics.mean_squared_error(ytest,pred_rf)
np.sqrt(metrics.mean_squared_error(ytest,pred_rf))



# SVR MODEL
pram_grid={'C':[0.1,1,10,100,1000], 'gamma':[1,0.1,0.01,0.001,0.0001]}
grid=GridSearchCV(SVR(),pram_grid,verbose=3)
grid.fit(Xtrain,ytrain)
grid.best_params_
#{'C': 1000, 'gamma': 0.01}
grid.best_estimator_
#SVR(C=1000, cache_size=200, coef0=0.0, degree=3, epsilon=0.1, gamma=0.01,
#    kernel='rbf', max_iter=-1, shrinking=True, tol=0.001, verbose=False)
pred_grid=grid.predict(Xtest)

metrics.mean_absolute_error(ytest,pred_grid)
metrics.mean_squared_error(ytest,pred_grid)
np.sqrt(metrics.mean_squared_error(ytest,pred_grid))
#6.0520296890047245


# GENERATING PICKLE FILE (SERIALIZATION) :
pickle.dump(knn_model, open('model.pkl', 'wb'))

model=pickle.load(open('model.pkl','rb'))
print(model.predict([[12.17,0.017,94.42,21.47,23.3,6.67]]))
