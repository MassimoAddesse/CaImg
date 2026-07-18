from profilers.profiler1 import Profiler1
from profilers.profiler2 import Profiler2
from profilers.profiler3 import profiler3
from models import AnalysisConfig


class CalciumAnalysis:

    def __init__(
        self,
        config: AnalysisConfig
    ):
        
        self.config = config

        self.profiler1 = Profiler1(
            config
        )

        self.profiler2 = Profiler2(
            config
        )
        #self.profiler3 = profiler3(
        #    config
        #)

    def run(self, fluorescence):

        p1_results = self.profiler1.run(
            fluorescence
        )

        p2_results = self.profiler2.run(
            p1_results[
                "active_cells_dff_df"
            ],
            p1_results[
                "events"
            ]
        )

        #p3_results = self.profiler3.run(
        #    filtered_dff,
        #     events
        #)

        return {
            "profiler1": p1_results,
            "profiler2": p2_results,
            #"profiler3": p3_results
        }