import sqlite3
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

def load_data(db_path, table_name):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name};", conn)
    conn.close()
    return df

def preprocess_data(df):
    df = df.drop(['ProjectName'], axis=1)
    df['TestPriority'] = df['TestPriority'].str.strip().str.title()
    priority_map = {
        'Low': 1, 'Minor': 1,
        'Medium': 2,
        'High': 3, 'Major': 3,
        'Very High': 3, 'Critical': 3
    }
    df['TestPriority'] = df['TestPriority'].map(priority_map)

    mask = df['Result'].isin(['PASS', 'FAIL'])
    df_filtered = df.loc[mask].copy()
    df_filtered['Result'] = df_filtered['Result'].map({'PASS': 0, 'FAIL': 1}).astype(int)
    
    return df_filtered, mask

def encode_features(train_df, test_df):
    encoder = OneHotEncoder(sparse_output=True, handle_unknown='ignore')
    X_train_encoded = encoder.fit_transform(train_df)
    X_test_encoded = encoder.transform(test_df) ##prevents data leakage
    return X_train_encoded, X_test_encoded, encoder

def train_models(X_train, y_train, X_test, y_test):
    models = {
        "Logistic Regression": LogisticRegression(multi_class="ovr", max_iter=1000),
        "Gradient Boost": GradientBoostingClassifier()
    }

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        print(f"\n{name}")
        print("Training Accuracy:", accuracy_score(y_train, y_train_pred))
        print("Training Confusion Matrix:\n", confusion_matrix(y_train, y_train_pred))
        print("Test Accuracy:", accuracy_score(y_test, y_test_pred))
        print("Test Confusion Matrix:\n", confusion_matrix(y_test, y_test_pred))
        print("-" * 40)
    
    return models

def assign_rank(prob):
    if prob >= 0.8:
        return 1
    elif prob >= 0.6:
        return 2
    elif prob >= 0.4:
        return 3
    elif prob >= 0.2:
        return 4
    else:
        return 5

def add_ranks(models, X_all, df, mask):
    for name, model in models.items():
        probs = model.predict_proba(X_all)
        probabilities = probs[:, 1]
        ranks = [assign_rank(p) for p in probabilities]
        df[f"Ranks by {name}"] = np.nan
        df.loc[mask, f"Ranks by {name}"] = ranks
    return df

def display_rank_summary(df):
    print(df['Ranks by Logistic Regression'].value_counts())
    print(df['Ranks by Gradient Boost'].value_counts())
    return df[["TestId", "Ranks by Logistic Regression", "Ranks by Gradient Boost"]]

def get_ranked_dataframe():
    df = load_data("dummy.sqlite3", "regression")
    df_filtered, mask = preprocess_data(df)
    
    y = df_filtered['Result']
    X = df_filtered.drop('Result', axis=1)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train, X_test, encoder = encode_features(X_train_raw, X_test_raw)
    models = train_models(X_train, y_train, X_test, y_test)

    X_all_encoded = encoder.transform(X)

    df_ranked = add_ranks(models, X_all_encoded, df, mask)
    summary_df = display_rank_summary(df_ranked)
    return df_ranked

if __name__ == "__main__":
    get_ranked_dataframe()
