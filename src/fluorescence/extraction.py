import numpy as np
import pandas as pd

def extract_fluorescence(
        stack: np.ndarray,
        masks: np.ndarray
) -> pd.DataFrame:

    """
    Extract mean fluorescence for every segmented cell in every frame.

    Parameters
    ----------
    stack: np.ndarray
        TIFF image stack with shape:
            (n_frames, height, width)

    masks: np.ndarray
        Cellpose segmentation mask with shape:
            (height, widht)
        Background must be 0.
        Cell labels should be 1, 2, 3, ..., n

    Returns
    -------
    pd.DataFrame
        Raw fluorescence.

        Rows    = frames
        Columns = ROIs
    """

    if stack.ndim != 3:
        raise ValueError(
            f"Expected stack with 3 dimensions"
            f"(frames, height, width), got {stack.shape}"
        )

    if masks.ndim != 2:
        raise ValueError(
            f"Expected 2D segmentation mask, got {masks.shape}"
        )

    if stack.shape[1:] != masks.shape:
        raise ValueError(
            "Image dimensions and mask dimensions do not match: "
            f"stack = {stack.shape[1:]}, masks = {masks.shape}"
        )

    n_frames = stack.shape[0]
    n_cells = int(np.max(masks))

    fluorescence = np.zeros(
        (n_frames, n_cells),
        dtype = float
    )

    cell_coordinates = {}

    for cell_id in range(1, n_cells + 1):

        coordinates = np.where(
            masks == cell_id
        )
        
        cell_coordinates[cell_id] = coordinates
        
    for frame_idx in range(n_frames):

        frame = stack[frame_idx]

        for cell_id, coordinates in cell_coordinates.items():

            fluorescence[
                frame_idx,
                cell_id - 1
            ] = np.mean(frame[coordinates])

    columns = [
        f"ROI_{cell_id}"
        for cell_id in range(1, n_cells + 1)
    ]

    return pd.DataFrame(
        fluorescence,
        columns = columns
    )



