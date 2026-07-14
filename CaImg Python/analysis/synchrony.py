from collections import Counter

def synchrony_type1(
        on_matrix
):
    
    """
    Compute frame-wise network synchrony.

    Parameters
    ----------
    on_matrix : np.ndarray

        Matrix of shape:
            (n_frames, n_cells)

        containing ON/OFF states.

    Returns
    -------
    np.ndarray
        Fraction of active neurons
        at each frame.

    Notes
    -----
    Synchrony is computed as:

        active_cells / total_cells
    """

    active_fraction = (
        on_matrix.sum(axis = 1)
        /
        on_matrix.shape[1]
    )

    return active_fraction

def real_coactivity(
        on_matrix
):
    
    """
    Compute the observed coactivity
    distribution.

    Parameters
    ----------
    on_matrix : np.ndarray
        Boolean ON/OFF activity matrix.

    Returns
    -------
    dict
        Dictionary where:

        key:
            number of active cells

        value:
            number of frames

    Notes
    -----
    This corresponds to the 'real'
    coactivity distribution used in
    synchrony analysis.
    """
    k = on_matrix.sum(axis = 1)

    return dict(
        Counter(k)
    )

def expected_coactivity():
    pass

def synchrony_type2():
    pass