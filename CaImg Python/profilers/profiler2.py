from models import Event

from analysis.event_kinetics import (
    rise_time,
    decay_time,
    rise_speed,
    decay_speed,
    event_peak,
    event_integral,
    event_std
)

import numpy as np


class Profiler2:

    """
    Event morphology profiler.

    This profiler computes event-level 
    descriptors, including:

    1. Peak amplitude

    2. Event integral (AUC) 

    3. Rise time

    4. Decay time   

    5. Rise speed

    6. Decay speed

    7. Event variability (std)
    """

    def __init__(
            self,
            rise_fraction = 0.9,
            decay_fraction = 0.9
    ):
        
        self.rise_fraction = rise_fraction
        self.decay_fraction = decay_fraction

    def run(
            self,

            filtered_dff,

            events
    ):
        """
        Analyse all detected events and
        compute event kinetics.

        Parameters
        ----------
        dff_matrix : np.ndarray
            Complete dF/F0 matrix.

        events : dict
            Dictionary of detected events
            intervals for each neuron.

        Returns
        -------
        list[Event]
            List of Event objects.
        """
        
        all_events = []

        for cell_id, cell_events in events.items():
            
            trace = (
                filtered_dff[:, cell_id]
            )

            for start, end in cell_events:

                event_trace = (
                    trace[start:end + 1]
                )

                peak = event_peak(
                    event_trace
                )

                integral = event_integral(
                    event_trace
                )

                std = event_std(
                    event_trace
                )

                rt = rise_time(

                    event_trace,

                    self.rise_fraction
                )

                dt = decay_time(
                    event_trace,

                    self.decay_fraction
                )
                
                rs = rise_speed(
                    peak,
                    rt
                )

                ds = decay_speed(
                    peak,
                    dt
                )


                event = Event(
                    cell_id = cell_id,

                    start_frame = start,

                    end_frame = end,

                    peak = peak,

                    integral = integral,

                    rise_time = rt,

                    decay_speed = ds,
                    
                    event_std = std
                )

                all_events.append(
                    event
                )

        return all_events