
import pandas as pd 
from typing import Tuple, Any 

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score, matthews_corrcoef


def train_models(dtable: pd.DataFrame, response: str, test_size: float=0.1, balanced: bool=True) -> Tuple: 
    # train test split
    X_train, X_test, y_train, y_test = train_test_split(dtable.drop(columns=[response]), dtable[response], test_size=test_size, random_state=42)

    # training, feature importance, performance estimation
    dt_mseries, dt_sframe =  _train_decision_tree(X_train, X_test, y_train, y_test, balanced=balanced)
    lr_mseries, lr_sframe =  _train_logistic_regressor(X_train, X_test, y_train, y_test, balanced=balanced)
    return dt_sframe, dt_mseries, lr_sframe, lr_mseries
    
def _train_decision_tree(
    X_train: pd.DataFrame, 
    X_test: pd.DataFrame, 
    y_train: pd.Series, 
    y_test: pd.Series, 
    balanced: bool
    ) -> Tuple[pd.Series, pd.DataFrame]:
    
    ### DECISION TREE ###
    # fit model
    # nsamples = int(X_train.shape[0] * 0.8)
    class_weight = 'balanced_subsample' if not balanced else None
    # class_weight = {0: 0.001, 1: 0.999} if not balanced else None
    clf = RandomForestClassifier(
        n_estimators=10, 
        # max_samples=nsamples, 
        criterion='entropy', 
        max_depth=6, 
        min_samples_leaf=5,
        class_weight=class_weight
    )
    clf.fit(X_train, y_train)

    # metrics 
    mseries = _calc_performance_metrics(clf, X_test, y_test)

    # feature importances
    sframe = pd.DataFrame({
        'Feature': X_train.columns,
        'Importance': clf.feature_importances_,
    })
    sframe = sframe.set_index('Feature')
    sframe = sframe.sort_values(by='Importance', ascending=False)
    return mseries, sframe

def _train_logistic_regressor(
    X_train: pd.DataFrame, 
    X_test: pd.DataFrame, 
    y_train: pd.Series, 
    y_test: pd.Series, 
    balanced: bool
    ) -> Tuple[pd.Series, pd.DataFrame]:

    ### LOGISTIC REGRESSION ###
    # scale continuous values
    continuous_cols = []
    for col in X_train.columns:
        if X_train[col].nunique() >= 3:
            continuous_cols.append(col)
    
    # print(continuous_cols)
    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    X_train_scaled[continuous_cols] = scaler.fit_transform(X_train[continuous_cols])
    X_test_scaled[continuous_cols] = scaler.transform(X_test[continuous_cols])

    # fit model
    class_weight = 'balanced' if not balanced else None
    # class_weight = {0: 0.001, 1: 0.999} if not balanced else None
    clf = LogisticRegression(class_weight=class_weight)
    clf.fit(X_train_scaled, y_train)

    # metrics
    mseries = _calc_performance_metrics(clf, X_test_scaled, y_test)

    # feature importance
    feature_names = X_train.columns
    coefficients = clf.coef_[0]  # Shape is (1, n_features) for binary classification
    sframe = pd.DataFrame({
        'Feature': feature_names,
        'Coefficient': coefficients,
        # 'Abs_Coefficient': np.abs(coefficients)
    })
    sframe = sframe.set_index('Feature')
    # sframe = sframe.sort_values(by='Abs_Coefficient', ascending=False)
    return mseries, sframe

def _calc_performance_metrics(clf: Any, X_test: pd.DataFrame, y_test: pd.Series) -> pd.Series:
    y_pred = clf.predict(X_test)
    mframe = pd.Series({
        'Precision': precision_score(y_test, y_pred),
        'Recall':    recall_score(y_test, y_pred),
        'Accuracy':  accuracy_score(y_test, y_pred),
        'F1':        f1_score(y_test, y_pred),
        'MCC':       matthews_corrcoef(y_test, y_pred),
    })
    return mframe


# ### STATSMODELS LOGIT ###
# logit_model = sm.Logit(y_train, sm.add_constant(X_train_scaled))
# result = logit_model.fit()
# print(result.summary())