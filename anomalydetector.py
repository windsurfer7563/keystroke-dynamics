
from sklearn.neural_network import MLPRegressor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from scipy import stats
import os
import pickle

class AnomalyDetector(object):
    def __init__(self,currentUser,clf):
        self.user = currentUser
        self.clf_type=clf
        self.clf={'NN': MLPRegressor(solver='sgd', activation='logistic', alpha=0.0001, tol=0.00001,
                   learning_rate_init=0.0001, max_iter=30000, momentum = 0.0003,
                    hidden_layer_sizes=(20), verbose=True),
                  'SVM': OneClassSVM(kernel="rbf")
                 }[clf]

        self.scaler = StandardScaler()

    def fit(self):
        userFilePath = (os.path.join("accounts", self.user + '.csv'))
        #Read File
        data = pd.read_csv(userFilePath,header=0)

        #навчаємо детектор -  в якості вектора результатів підсавляємо ветор X
        # навчаємо тільки на нормальних даних - біометрика паролей введених оригінальним користувачем

        #print(data)

        #self.scaler.fit(data)
        #X_train = self.scaler.transform(data)
        X_train = data
        dummyres = {'NN': self.clf.fit(X_train,X_train),
        'SVM': self.clf.fit(X_train)
        }[self.clf_type]

        self.treshold = 0
        if self.clf_type=='NN':
            #для визначення treshold визначимо відстані на тренувальній вибірці
            dist_train=np.linalg.norm(X_train-self.clf.predict(X_train),axis=1)
            self.treshold=np.mean(dist_train)+2*np.std(dist_train)
            print('Treshold: %.3f' % self.treshold)

        #serialization
        userFilePath =  (os.path.join("accounts", self.user + '_' + self.clf_type + '.dat'))
        pickle.dump(self,open(userFilePath,"wb"))


    def predict(self, keys_data):
         #print(keys_data)
         #keys_data = self.scaler.transform(keys_data.reshape(1,-1))
         keys_data = keys_data.reshape(1,-1)
         print(keys_data)

         # обчислюємо відстань поміж тестовими часовими  векторами та векторами отриманими на виході нейронної мережі
         # чим більша відстань тим більша ймовірність що дані не належать ритму друку оригінального користувача

         dist = 0
         if self.clf_type=='NN':
             dist = np.linalg.norm(keys_data - self.clf.predict(keys_data),axis=1)
             print('Dist: %.3f, Treshold: %.3f' % (dist,self.treshold))

         return {'NN': np.where(dist < self.treshold,0,1),
                 'SVM': self.clf.predict(keys_data)
                }[self.clf_type]
