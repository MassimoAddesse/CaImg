from io.excel_loader import load_fluorescence
from io.controls_loader import load_controls

from analysis.thresholding import compute_threshold

from pipeline import calciumanalysis

filename = "treated.csv"

controls = load_controls(
    "controls/"
)

threshold = compute_threshold(
    controls,
    factor = 4
)

recording = load_fluorescence(
    filename
)

analysis = calciumanalysis(
    threshold = threshold
)

results = analysis.run(
    recording
)

export_events(
    results["profiler2"],
    "events.xlsx"
)