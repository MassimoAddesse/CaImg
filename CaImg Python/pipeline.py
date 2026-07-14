from profilers.profiler1 import profiler1
from profilers.profiler2 import profiler2
from profilers.profiler3 import profiler3


class calciumanalysis:

    def __init__(
            self,
            threshold,
            half_window = 20
    ):
        
        self.threshold = threshold 

        self.profiler1 = profiler1(
            threshold = threshold,
            half_window = half_window
        )

        self.profiler2 = profiler2()

        self.profiler3 = profiler3()

    def run(self, fluorescence):

        p1_results = self.profiler1.run(
            fluorescence
        )

        p2_results = self.profiler2.run(
            p1_results["filtered_dff"],
            p1_results["events"]
        )

        p3_results = self.profiler3.run(
            p1_results["filtered_dff"],
            p1_results["events"]
        )
            
        return {
            "profiler1": p1_results,
            "profiler2": p2_results,
            "profiler3": p3_results
        }