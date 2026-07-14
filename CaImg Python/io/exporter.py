import pandas as pd

def export_events(
        events,
        output
):
    
    pd.DataFrame(events).to_excel(
        output,
        index = False
    )