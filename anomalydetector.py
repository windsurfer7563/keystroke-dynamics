
from sklearn.neural_network import MLPRegressor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import *
from scipy.spatial.distance import chebyshev
from scipy.spatial.distance import mahalanobis
from scipy import linalg
import numpy as np
import pandas as pd
from scipy import stats
import os
import pickle

class AnomalyDetector(object):
    def __init__(self,currentUser,clf):
        self.user = currentUser
        self.clf_type=clf
        self.clf={'NN': MLPRegressor(learning_rate_init=0.0001, max_iter=200000, alpha=0.01,
                    hidden_layer_sizes=(20), verbose=True),
                  'SVM': OneClassSVM(kernel="rbf")
                 }[clf]

        #self.scaler = RobustScaler()
        self.scaler = StandardScaler()
        '''
        MLPRegressor(solver='sgd', activation='logistic', alpha=0.00001, tol=0.000001,
           learning_rate_init=0.0001, max_iter=200000, momentum = 0.00003,
            hidden_layer_sizes=(20), verbose=False),

        '''


    def fit(self):
        userFilePath = (os.path.join("accounts", self.user + '.csv'))
        #Read File
        data = pd.read_csv(userFilePath,header=0)

        #навчаємо детектор -  в якості вектора результатів підсавляємо ветор X
        # навчаємо тільки на нормальних даних - біометрика паролей введених оригінальним користувачем


        self.scaler.fit(data)
        X_train = self.scaler.transform(data)
        #X_train = data

        if self.clf_type == 'NN':
            self.clf.fit(X_train, X_train)
        else:
            self.clf.fit(X_train)

        print("fitted OK")

        self.treshold = 0
        if self.clf_type=='NN':
            #для визначення treshold визначимо відстані на тренувальній вибірці

            #dist_train=np.linalg.norm(X_train-self.clf.predict(X_train),axis=1)
            dist_train=[]
            predicted=self.clf.predict(X_train)



            for i in (range(X_train.shape[0])):
                dist_train.append(euclidean(predicted[i],X_train[i]))
                #dist_train.append(chebyshev(predicted[i],X_train[i]))
                #X = predicted
                #V = np.cov(X.T)
                #VI = np.linalg.inv(V)
                #dist_train.append(mahalanobis(predicted[i], X_train[i], VI))


            print("Max Dist Train: {0:.4f}".format(max(dist_train)))
            #print(dist_train)
            self.treshold=np.mean(dist_train) + 4 * np.std(dist_train)
            print('Treshold: %.3f' % self.treshold)

        #serialization
        userFilePath =  (os.path.join("accounts", self.user + '_' + self.clf_type + '.dat'))
        pickle.dump(self, open(userFilePath,"wb"))


    def predict(self, keys_data):
         #print(keys_data)
         keys_data = self.scaler.transform(keys_data.reshape(1,-1))
         #print(keys_data)

         # обчислюємо відстань поміж тестовими часовими  векторами та векторами отриманими на виході нейронної мережі
         # чим більша відстань тим більша ймовірність що дані не належать ритму друку оригінального користувача

         dist = 0
         if self.clf_type=='NN':
             #dist = np.linalg.norm(keys_data - self.clf.predict(keys_data),axis=1)
             dist = euclidean(keys_data, self.clf.predict(keys_data))
             #dist = chebyshev(keys_data, self.clf.predict(keys_data))



             print('Dist: %.3f, Treshold: %.3f' % (dist,self.treshold))

         return ({'NN': np.where(dist < self.treshold,0,1),
                 'SVM': self.clf.predict(keys_data)
                }[self.clf_type], dist, self.treshold)
