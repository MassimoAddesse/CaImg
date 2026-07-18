import numpy as np

import pandas as pd

from analysis import (
    local_min_f0,
    compute_dff,
    detect_on_states,
    extract_events,
    extract_iei,
    real_coactivity
)

from models import AnalysisConfig

from analysis import synchrony_type1

class Profiler1:

    """
    Fluorescence preprocessing and event detection profiler.

    This profiler performs:

    1. Local baseline estimation (F0) using a rolling minimum window.

    2. dF/F0 normalization.

    3. Event detection.

    4. Active cell identification.

    5. IEI extraction.

    6. Synchrony estimation.

    """
    
    def __init__(
            self,
            config : AnalysisConfig
    ):
        
        self.config = config

    def run(
            self,
            fluorescence : pd.DataFrame
    ) -> dict:
        """
        Extecture the complete Profiler1 workflow.

        Parameters
        ----------
        fluorescence : pd.DataFrame
            
            DataFrame containing raw fluorescence traces.

        Rows:
            Frames.

        Columns:
            Cells

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

        dff_df = pd.DataFrame(
            index = fluorescence.index
        )

        active_cells = []

        events = {}

        iei = {}

        summary_rows = []

        on_matrix = np.zeros(
           (n_frames, n_cells),
            dtype = bool
        )

        for col_idx, cell_name in enumerate(
            fluorescence.columns
        ):
            
            signal = fluorescence[
                cell_name
            ].to_numpy()

            f0 = local_min_f0(
                signal,
                half_window = self.config.half_window,
                edge_margin = self.config.edge_margin
            )

            dff = compute_dff(
                signal, 
                f0
            )

            dff_df[cell_name] = dff

            valid_mask = ~np.isnan(
                dff
            )

            valid_dff = dff[
                valid_mask
            ]

            if len(valid_dff) == 0:

                events[cell_name] = []

                iei[cell_name] = []

                summary_rows.append(
                    {
                        "Cell": cell_name,
                        "Events": 0,
                        "Total_IEI_Frames": 0,
                        "Active": False
                    }
                )

                continue

            on = detect_on_states(
                valid_dff,
                self.config.threshold
            )

            raw_events = extract_events(
                on
            )

            cell_events = [

                (
                    start + self.config.edge_margin,
                    end + self.config.edge_margin
                )

                for start, end
                in raw_events
            ]

            raw_iei = extract_iei(
                on
            )
    
            cell_iei = [

                (
                    start + self.config.edge_margin,
                    end + self.config.edge_margin
                )

                for start, end
                in raw_iei
            ]

            n_events = len(
                cell_events
            )

            iei_lengths = [
                end - start + 1

                for start, end

                in cell_iei
            ]

            total_iei_frames = sum(
                iei_lengths
            )

            is_active = (
                n_events > 0
            )

            if is_active:

                active_cells.append(
                    cell_name
                )

                reconstructed_on = np.zeros(
                    n_frames,
                    dtype = bool
                )

                reconstructed_on[
                    valid_mask
                ] = on

                on_matrix[
                    :,

                    col_idx
                ] = reconstructed_on

            events[
                cell_name
            ] = cell_events

            iei[
                cell_name
            ] = cell_iei

            summary_rows.append(
                {
                    "Cell": cell_name,
                    "Events": n_events,
                    "Total_IEI_Frames": total_iei_frames,
                    "Active": is_active
                }
            )

        summary_df = pd.DataFrame(
            summary_rows
        )

        active_dff_df = dff_df[
            active_cells
        ]

        if len(active_cells) > 0:

            active_indices = [
                fluorescence.columns.get_loc(cell)
                for cell in active_cells
            ]

            sync1 = synchrony_type1(

                on_matrix[
                    :, 
                    active_indices
                ]    
            )

            sync2 = real_coactivity(

                on_matrix[
                    :, 
                    active_indices
                ]
            )

        else:

            sync1 = None
            sync2 = None

        return {
            "all_cells_dff_df": dff_df,

            "active_cells_dff_df": active_dff_df,

            "summary": summary_df,

            "active_cells": active_cells,

            "events": events,

            "iei": iei,

            "sync_type1": sync1,

            "sync_type2": sync2

        }