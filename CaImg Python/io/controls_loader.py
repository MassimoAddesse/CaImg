from pathlib import Path

from .excel_loader import (
    load_fluorescence
)

def load_controls(
        folder
):
    
    controls = []

    for file in Path(folder).glob(
        "*.csv"
    ):
        
        controls.append(
            load_fluorescence(file)
        )

    return controls