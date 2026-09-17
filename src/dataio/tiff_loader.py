import os 
import tifffile
import numpy as np

def load_tiff(tiff_path: str) -> np.ndarray:
    if not os.path.exists(tiff_path):
        raise FileNotFoundError(
            f"TIFF file does not exists: {tiff_path}"
        )

    stack = tifffile.imread(tiff_path)

    if stack.ndim != 3:
        raise ValueError(
            f"Expected a 3d TIFF stack"
            f"(frames, height, width), got shape {stack.shape}"
        )

    return stack