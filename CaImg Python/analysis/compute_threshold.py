import numpy as np

def compute_threshold(
        controls,
        factor = 3
):
    
    """
    Compute a global event-detectionthreshold 
    from control recordings.

    Parameters
    ----------
    controls : list of np.ndarray
        List of control fluorescence traces.

        Each recording must have shape:

            (n_frames, n_cells)

    factor : float, optional
        Multiplicative factor applied to the
        baseline estimate.

    Returns
    -------
    float
        Global threshold used for event detection.
        
    """
    rec_thresholds = []

    for rec in controls:

        neuron_medians = np.median(
            rec,
            axis = 0
        )

        rec_threshold = np.mean(
            neuron_medians
        )

        rec_thresholds.append(
            rec_threshold
        )


    baseline = np.mean(
        rec_thresholds
    )

    return baseline * factor