from collections import Counter
import numpy as np


def overlap(
        start1,
        end1,
        start2,
        end2
):
    """
    Determine whether two event intervals overlap.

    Parameters
    ----------
    start1 : int
        Start frame of the first event.

    end1 : int
        End frame of the first event.

    start2 : int
        Start frame of the second event.

    end2 : int
        End frame of the second event.

    Returns
    -------
    bool
        True if the two intervals overlap,
        False otherwise.
    """

    return (
        start1 <= end2
        and
        start2 <= end1
    )


def event_coactivity(
        events
):
    """
    Compute event-based coactivity across neurons.

    Parameters
    ----------
    events : dict
        Dictionary where:

            key:
                neuron index

            value:
                list of tuples

        Each tuple represents an event:

            (start_frame, end_frame)

    Returns
    -------
    dict
        Distribution of event coactivity.

        key:
            number of coactive neurons

        value:
            number of detected events

    Notes
    -----
    For each event, all neurons containing
    at least one overlapping event are counted.
    """

    counts = []

    for cell_id, cell_events in events.items():

        for start, end in cell_events:

            coactive_cells = {cell_id}

            for other_cell, other_events in events.items():

                if other_cell == cell_id:
                    continue

                for s2, e2 in other_events:

                    if overlap(
                        start,
                        end,
                        s2,
                        e2
                    ):

                        coactive_cells.add(
                            other_cell
                        )

                        break

            counts.append(
                len(coactive_cells)
            )

    return dict(
        sorted(
            Counter(counts).items()
        )
    )


def real_coactivity(
        on_matrix
):
    """
    Compute the observed coactivity distribution.

    Parameters
    ----------
    on_matrix : np.ndarray

        Boolean activity matrix with shape:

            (n_frames, n_cells)

    Returns
    -------
    dict

        key:
            number of active neurons

        value:
            probability of observing that
            level of coactivity

    Notes
    -----
    The observed distribution is calculated
    directly from the recorded activity matrix.
    """

    k = on_matrix.sum(
        axis=1
    )

    counts = Counter(k)

    total_frames = len(k)

    return {
        active_cells:
        n_frames / total_frames

        for active_cells,
        n_frames

        in sorted(counts.items())
    }


def expected_coactivity(
        on_matrix
):
    """
    Compute the expected coactivity distribution
    using a Poisson-Binomial model.

    Parameters
    ----------
    on_matrix : np.ndarray

        Boolean activity matrix with shape:

            (n_frames, n_cells)

    Returns
    -------
    dict

        key:
            number of active neurons

        value:
            probability expected under
            independent activity

    Notes
    -----
    Each neuron is assigned its own
    activation probability:

        p_i = fraction of ON frames

    The resulting distribution corresponds
    to a Poisson-Binomial random variable.
    """

    p = np.mean(
        on_matrix,
        axis=0
    )

    n_cells = len(p)

    pmf = np.zeros(
        n_cells + 1
    )

    pmf[0] = 1.0

    for pi in p:

        new_pmf = np.zeros(
            n_cells + 1
        )

        for k in range(n_cells):

            new_pmf[k] += (
                pmf[k] * (1 - pi)
            )

            new_pmf[k + 1] += (
                pmf[k] * pi
            )

        pmf = new_pmf

    return {
        k: pmf[k]
        for k in range(
            n_cells + 1
        )
    }


def synchrony_type2(
        on_matrix
):
    """
    Compare observed and expected coactivity.

    Parameters
    ----------
    on_matrix : np.ndarray

        Boolean activity matrix with shape:

            (n_frames, n_cells)

    Returns
    -------
    dict

        key:
            number of active neurons

        value:
            observed / expected ratio

    Notes
    -----
    Interpretation:

        ratio > 1
            more synchronous activity than expected

        ratio = 1
            activity compatible with independence

        ratio < 1
            less synchrony than expected
    """

    observed = real_coactivity(
        on_matrix
    )

    expected = expected_coactivity(
        on_matrix
    )

    score = {}

    for k in expected:

        exp = expected[k]

        if exp <= 0:
            continue

        score[k] = (
            observed.get(k, 0)
            /
            exp
        )

    return score

def synchrony_type1(
        on_matrix
):
    """
    Fraction of frames containing
    at least one active neuron.
    """

    active_frames = np.sum(
        on_matrix,
        axis=1
    )

    return np.mean(
        active_frames > 0
    )