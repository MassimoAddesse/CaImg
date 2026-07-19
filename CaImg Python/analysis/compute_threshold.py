import numpy as np

from .normalization import (
    local_min_f0,
    compute_dff
)


def compute_threshold(
        controls,
        factor=4,
        half_window=20,
        edge_margin=50
):
    """
    Compute a global event-detection threshold
    from control recordings.

    Parameters
    ----------
    controls : list[np.ndarray]
        List of control fluorescence recordings.

        Each recording must have shape:

            (n_frames, n_cells)

    factor : float, optional
        Multiplicative factor applied to
        the baseline estimate.

    half_window : int, optional
        Half-width of the rolling baseline
        window used for F0 estimation.

    edge_margin : int, optional
        Number of frames excluded from the
        beginning and end of the recording.

    Returns
    -------
    float
        Event-detection threshold expressed
        in dF/F0 units.
    """

    if not controls:

        raise ValueError(
            "controls cannot be empty"
        )

    std_medians = []

    for rec in controls:

        cell_stds = []

        for cell in rec.columns:

            signal = (
                rec[cell]
                .to_numpy()
            )

            f0 = local_min_f0(
                signal,
                half_window=half_window,
                edge_margin=edge_margin
            )

            dff = compute_dff(
                signal,
                f0
            )

            valid_dff = dff[
                ~np.isnan(dff)
            ]

            if len(valid_dff) == 0:
                continue

            cell_stds.append(
                np.std(valid_dff)
            )

        if len(cell_stds) == 0:
            continue

        std_medians.append(
            np.median(
                cell_stds
            )
        )

    if len(std_medians) == 0:

        raise ValueError(
            "No valid control traces found"
        )

    baseline = np.median(
        std_medians
    )

    return float(
        baseline * factor
    )