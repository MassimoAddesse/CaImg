Python application for analyzing calcium-imaging recordings from neuronal cultures. It combines cell segmentation, fluorescence extraction, calcium-event detection, and single-cell and network analysis.

The project aims to make the analysis workflow accessible through a graphical interface while keeping the underlying methods configurable and transparent.

Analysis workflow
1. Load recordings: import a TIFF stack with dimensions corresponding to frames, height, and width.
2. Segment cells: identify regions of interest using Cellpose.
3. Extract fluorescence: calculate mean fluorescence within each ROI for every frame.
4. Normalize traces: estimate the fluorescence baseline and calculate ΔF/F.
5. Detect calcium events: identify candidate events using the selected detection method.
6. Calculate metrics: summarize individual events, cellular activity, and population dynamics.

Detection methods

The code includes:

Adaptive STD thresholding
Adaptive MAD thresholding
Savitzky–Golay filtering with peak prominence

Detection parameters are defined in config/analysis_config.py.

Analysis outputs

Implemented calculations include:

Event amplitude, duration, and area under the curve
Rise and decay times and speeds
Event frequency and inter-event intervals
Pearson and Spearman correlations
Population activity, coactivity, and event synchrony

An Excel export backend is included. Export availability depends on the application entry point; integration with the newer GUI is still under development.

Running the application

Clone the repository:

git clone https://github.com/MassimoAddesse/CaImg.git
cd CaImg

From a Python environment containing the required dependencies, launch the PySide6 interface:

python main_gui.py

An earlier Tkinter interface is available through:

python main.py

Main dependencies include NumPy, pandas, SciPy, tifffile, Cellpose, PySide6, and openpyxl. A tested, version-pinned installation specification is planned.

Set the recording frame rate correctly before analysis. Other parameters, including segmentation diameter and detection thresholds, are configured in config/analysis_config.py.

Development status

CaImg is under active development and validation.

Current priorities include repairing detector inconsistencies, improving the separation and measurement of overlapping events, completing GUI export, and expanding automated tests.

Synthetic tests have identified limitations involving weak events, correlated noise, and overlapping event boundaries. Results should be checked against representative traces and manually reviewed events before biological interpretation.

Spike-inference modules are experimental and are not yet integrated into the main workflow.

Repository organization
config/ — analysis parameters
gui/ — graphical interface and analysis worker
src/ — processing and analysis modules
main_gui.py — PySide6 application entry point
main.py — earlier Tkinter application entry point
CaImg Python/ — previous implementation retained in the repository
