"""
train_priority_model.py

Loads the sklearn breast cancer dataset, synthesizes a 3-class 'priority' label, preprocesses, trains a RandomForestClassifier,
evaluates accuracy and F1-score, and saves the trained model to model.pkl.
"""
import joblib
import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def create_priority_labels(df: pd.DataFrame) -> pd.Series:
    # Use 'mean radius' as a proxy to synthesize priority: top 33% -> high, middle -> medium, bottom -> low
    scores = df['mean radius']
    q1 = np.percentile(scores, 33)
    q2 = np.percentile(scores, 66)
    def map_priority(x):
        if x <= q1:
            return 'low'
        elif x <= q2:
            return 'medium'
        else:
            return 'high'
    return scores.apply(map_priority)


def main():
    data = load_breast_cancer(as_frame=True)
    X = data.frame.drop(columns=['target'])
    # synthesize priority labels
    y = create_priority_labels(X)

    # encode labels
    label_map = {'low':0, 'medium':1, 'high':2}
    y_enc = y.map(label_map)

    # train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y_enc, test_size=0.2, random_state=42, stratify=y_enc)

    # pipeline: scaler + random forest
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('rf', RandomForestClassifier(n_estimators=200, random_state=42, class_weight='balanced'))
    ])

    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average='macro')

    print('Accuracy:', acc)
    print('F1 (macro):', f1_macro)
    print('\nClassification report:')
    print(classification_report(y_test, y_pred, target_names=['low','medium','high']))

    # save model and label map
    joblib.dump({'pipeline': pipe, 'label_map': label_map}, 'model.pkl')
    print('Saved model to model.pkl')


if __name__ == '__main__':
    main()
