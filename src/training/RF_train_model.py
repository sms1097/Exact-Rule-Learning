import pandas as pd
import numpy as np
import pickle
from preprocess import load_data_class, model_report

from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split, RandomizedSearchCV
 
from sklearn.ensemble import  RandomForestClassifier



def train_model(management, discount):
    data = load_data_class(management, discount)

    scaler = RobustScaler()

    X = data.drop(['Voucher', 'Treatment', 'Salvage', 'TimeStep'], axis=1)
    X = scaler.fit_transform(X)

    y = data['Voucher']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

    # Random Search
    # Number of trees in random forest
    n_estimators = [int(x) for x in np.linspace(start = 5000, stop = 10000, num = 100)]
    # Number of features to consider at every split
    max_features = [int(x) for x in np.linspace(start=3, stop=X.shape[1], num=1)]
    # Maximum number of levels in tree
    max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
    max_depth.append(None)
    # Minimum number of samples required to split a node
    min_samples_split = [2, 5, 10]
    # Minimum number of samples required at each leaf node
    min_samples_leaf = [1, 2, 4]
    # Method of selecting samples for training each tree
    bootstrap = [True, False]

    # Create the random grid
    param_grid = {
        'n_estimators': n_estimators,
        'max_features': max_features,
        'max_depth': max_depth,
        'min_samples_split': min_samples_split,
        'min_samples_leaf': min_samples_leaf,
        'bootstrap': bootstrap,
        'class_weight': ['balanced', None]
    }

    f = RandomForestClassifier()
    rf = RandomizedSearchCV(f, param_grid, n_jobs=3)

    rf.fit(X_train, y_train)
    preds = rf.predict(X_test)
    train_preds = rf.predict(X_train)

    model_report(management, discount, preds, train_preds, y_test, y_train)

    with open('model/RF/' + discount + '/' + management, 'wb') as handle:
        pickle.dump(rf, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__": 
    mgmts = ['Comm-Ind', 'Heavy', 'HighGrade', 'Light', 'NoMgmt', 'Moderate']
    discounts = ['NoDR', 'DR1', 'DR3', 'DR5']
    for mgmt in mgmts:
        for discount in discounts:
            train_model(mgmt, discount)