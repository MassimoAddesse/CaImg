import numpy as np

from analysis import (
    local_min_f0,
    compute_dff,
    detect_on_states,
    extract_events,
    extract_iei,
    synchrony_type1,
    real_coactivity
)

class Profiler1:

    """
    Network activity profiler.
    
    This profiler performs:

    1. Baseline estimation (F0)
    2. dF/F0 computation
    3. Active cell detection
    4. Event extraction
    5. Inter-event interval (IEI) extraction
    6. Synchrony analysis
    """
    def __init__(
            self,
            threshold,
            half_window = 20
    ):
        
        self.threshold = threshold 
        self.half_window = half_window

    def run(self, fluorescence):
        """
        Extecture the complete Profiler1 workflow.

        Parameters
        ----------
        fluorescence : np.ndarray
            
            Raw fluorescence matrix:
                (n_frames, n_cells)

        Returns
        -------
        dict

            Dictionary containing:

            - dff : np.ndarray
                dF/F0 matrix for all cells.

            filtered_dff : np.ndarray
                dF/F0 matrix for active cells.

            - active_cells : list
                List of indices of active cells.

            - events : dict
                Dictionary of events for each active cell.

            - iei : dict
                Dictionary of inter-event intervals for each active cell.

            - sync_type1 : float
                Synchrony measure type 1.

            - sync_type2 : float
                Synchrony measure type 2.
        """
        n_frames, n_cells = fluorescence.shape 

        dff_matrix = np.zeros_like(
            fluorescence, 
            dtype = float
        )

        active_cells = []

        events = {}
        iei = {}

        on_matrix = np.zeros_like(
            fluorescence,
            dtype = bool
        )

        for cell_id in range(n_cells):

            signal = fluorescence[:, cell_id]

            f0 = local_min_f0(
                signal,
                self.half_window
            )

            dff = compute_dff(
                signal, 
                f0
            )

            dff_matrix[:, cell_id] = dff

            is_active = (
                np.max(dff)
                >=
                self.threshold
            )

            if is_active:

                active_cells.append(cell_id)

                on = detect_on_states(
                    dff,
                    self.threshold
                )

                on_matrix[:, cell_id] = on

                events[cell_id] = (
                    extract_events(on)
                )

                iei[cell_id] = (
                    extract_iei(on)
                )

        filtered_dff = dff_matrix[
            :,
            active_cells
        ]
        
        if len(active_cells) == 0:

            sync1 = None
            sync2 = None

        else:
            
            sync1 = synchrony_type1(
                on_matrix[:, active_cells]
            )

            sync2 = real_coactivity(
                on_matrix[:, active_cells]
            )

        return {
            "dff": dff_matrix,
            "filtered_dff": filtered_dff,
            "active_cells": active_cells,
            "events": events,
            "iei": iei,
            "sync_type1": sync1,
            "sync_type2": sync2
        }