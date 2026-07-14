import pandas as pd

def load_fluorescence(path):

    df = pd.read_excel(
        path,
        engine = "openpyxl"
    )

    return df.to_numpy()