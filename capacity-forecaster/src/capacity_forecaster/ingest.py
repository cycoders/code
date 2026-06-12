import pandas as pd

def load_series(path):
    df = pd.read_csv(path, parse_dates=[0])
    return df.iloc[:, 1].values