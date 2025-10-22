"""
fairness_audit.py

Loads model.pkl and runs a simple fairness audit. Since we don't have a real 'team' field,
we synthesize a `team` attribute and compute per-team accuracy and macro-F1. If AIF360
is available, compute statistical parity and disparate impact for the 'high' priority class.

The script writes `fairness_report.json` with the computed metrics.
"""
import json
import random
import joblib
import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import accuracy_score, f1_score

try:
    from aif360.datasets import BinaryLabelDataset
    from aif360.metrics import ClassificationMetric
    AIF360_AVAILABLE = True
except Exception:
    AIF360_AVAILABLE = False


def synthesize_team(n):
    # create 3 teams with imbalance
    teams = []
    for i in range(n):
        r = random.random()
        if r < 0.7:
            teams.append('team_A')
        elif r < 0.9:
            teams.append('team_B')
        else:
            teams.append('team_C')
    return np.array(teams)


def main():
    data = load_breast_cancer(as_frame=True)
    X = data.frame.drop(columns=['target'])
    model_bundle = joblib.load('model.pkl')
    pipe = model_bundle['pipeline']
    inv_label_map = {v:k for k,v in model_bundle['label_map'].items()}

    # create synthetic test set
    X_test = X.sample(200, random_state=42)
    teams = synthesize_team(len(X_test))
    # -- synthesize true priority labels using same logic as training --
    # Here we reuse 'mean radius' thresholds to create low/medium/high labels
    scores = X_test['mean radius']
    q1 = np.percentile(X['mean radius'], 33)
    q2 = np.percentile(X['mean radius'], 66)
    def map_priority_val(x):
        if x <= q1:
            return 'low'
        elif x <= q2:
            return 'medium'
        else:
            return 'high'
    y_true_names = scores.apply(map_priority_val)
    label_map = model_bundle.get('label_map', {'low':0,'medium':1,'high':2})
    inv_label_map = {v:k for k,v in label_map.items()}
    y_true_enc = y_true_names.map(label_map)

    # predictions
    y_pred_enc = pipe.predict(X_test)
    y_pred_names = [inv_label_map[int(v)] for v in y_pred_enc]

    # binary versions (high vs not-high) for parity metrics
    y_true_bin = np.array([1 if n=='high' else 0 for n in y_true_names])
    y_pred_bin = np.array([1 if n=='high' else 0 for n in y_pred_names])

    report = {}
    report['overall_accuracy'] = float(accuracy_score(y_true_enc, y_pred_enc))

    # per-team performance: compare true vs predicted
    team_metrics = {}
    for t in np.unique(teams):
        idx = np.where(teams==t)[0]
        if len(idx)==0:
            continue
        y_t = y_true_enc.iloc[idx]
        y_p = y_pred_enc[idx]
        acc = accuracy_score(y_t, y_p)
        f1 = f1_score(y_t, y_p, average='macro')
        team_metrics[t] = {'accuracy': float(acc), 'f1_macro': float(f1), 'support': int(len(idx))}
    report['per_team'] = team_metrics

    if AIF360_AVAILABLE:
        # create BinaryLabelDataset using true labels as 'label' and attach predictions as scores
        df = X_test.copy()
        df['team'] = teams
        df['label'] = y_true_bin
        df['score'] = y_pred_bin
        # BinaryLabelDataset expects protected attribute(s) as numeric or categorical columns
        dataset_true = BinaryLabelDataset(df=df, label_names=['label'], protected_attribute_names=['team'], favorable_label=1)
        # To compute classification metric, we need a dataset with predicted labels as 'score' or label; create a copy with predicted label
        df_pred = df.copy()
        df_pred['label'] = df['score']
        dataset_pred = BinaryLabelDataset(df=df_pred, label_names=['label'], protected_attribute_names=['team'], favorable_label=1)
        cm = ClassificationMetric(dataset_true, dataset_pred, unprivileged_groups=[{'team':'team_C'}], privileged_groups=[{'team':'team_A'}])
        report['aif360'] = {
            'statistical_parity_difference': cm.statistical_parity_difference(),
            'disparate_impact': cm.disparate_impact()
        }

    # -- manual parity metrics (works without AIF360) --
    # compute group positive rates (P(Y_hat=1 | group)) for teams
    df_pr = pd.DataFrame({'team': teams, 'y_true_bin': y_true_bin, 'y_pred_bin': y_pred_bin})
    group_rates = df_pr.groupby('team')['y_pred_bin'].mean().to_dict()
    # reference (privileged) group is team_A by convention
    priv_rate = float(group_rates.get('team_A', 0.0))
    unpriv_rate = float(group_rates.get('team_C', 0.0))
    # statistical parity difference = unprivileged - privileged
    spd = unpriv_rate - priv_rate
    # disparate impact = unprivileged / privileged (guard divide-by-zero)
    di = (unpriv_rate / priv_rate) if priv_rate > 0 else None
    report['parity'] = {
        'group_positive_rate': {k: float(v) for k,v in group_rates.items()},
        'statistical_parity_difference': float(spd),
        'disparate_impact': (float(di) if di is not None else None)
    }

    with open('fairness_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print('Wrote fairness_report.json')

if __name__ == '__main__':
    main()
