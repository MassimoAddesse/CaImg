import pandas as pd

def load_fluorescence(path):

    df = pd.read_csv(
        path,
        index_col = 0
    )

    df.index.name = "frame"

    df.columns = [
        f"Cell_{i}"
        for i in range(
            1,
            len(df.columns) + 1
        )
    ]

    return df