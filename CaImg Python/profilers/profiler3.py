import numpy as np


class profiler3:

    def renormalize_event(
            self,
            event_trace
    ):
        
        peak = np.max(
            event_trace
        )

        if peak == 0:

            return event_trace
        
        return event_trace / peak
    
    def compute_correlation_matrix(
            self,
            normalized_events
    ):
        
        return np.corrcoef(
            normalized_events
        )
    
    def run(
            self,
            filtered_dff,
            events
    ):
        
        normalized_events = []

        for cell_id, evs in events.items():

            trace = (
                filtered_dff[:, cell_id]
            )

            for start, end in evs:

                event_trace = (
                    trace[start:end+1]
                )

                normalized = (
                    self.renormalize_event(
                        event_trace
                    )
                )

                normalized_events.append(
                    normalized
                )

        correlation_matrix = (
            self.compute_correlation_matrix(
                normalized_events
            )
        )

        return {

            "normalized_events":
            normalized_events,

            "correlation_matrix":
            correlation_matrix
        }