import numpy as np
import pandas as pd


class Profiler3:

    def run(
            self,
            active_cells_dff_df: pd.DataFrame
    ):
        
        working_df = active_cells_dff_df.round(3)

        abs_df = working_df.abs()

        renorm_df = abs_df.div(
            abs_df.max(),
            axis = 1
        )

        corr_matrix = renorm_df.corr(
            method = "pearson"
        )

        cell_stats = []

        for cell in corr_matrix.columns:

            vals = corr_matrix[cell].drop(
                labels = [cell]
            )

            cell_stats.append(
                {

                    "Cell" : cell,

                    "MedianCorrelation" : vals.median(),

                    "MeanCorrelation" : vals.mean()
        
                }
            )

            cell_summary = pd.DataFrame(
                cell_stats
            )

            best_cell_row = (
                        cell_summary
                        .sort_values(
                            "MeanCorrelation",
                            ascending=False
                        )
                        .iloc[0]
                    )

            worst_cell_row = (
                        cell_summary
                        .sort_values(
                            "MeanCorrelation",
                            ascending=True
                        )
                        .iloc[0]
                    )

            upper_mask = np.triu(
                np.ones(
                    corr_matrix.shape
                ),
                k=1
            ).astype(bool)

            pairwise_corrs = corr_matrix.to_numpy()[
                np.triu_indices_from(
                    corr_matrix,
                    k=1
                )
            ]

            quantiles = np.arange(
                0,
                1.1,
                0.1
            )

            correlation_distribution = (
                pd.DataFrame(
                    {

                        "Rank": quantiles, 

                        "Quantile":
                            np.quantile(
                                pairwise_corrs,
                                quantiles
                            )
                    }
                )
            )

            network_summary = pd.DataFrame(
                [
                    {
                        "ActiveCells":
                            len(
                                renorm_df.columns
                            ),

                        "MeanNetworkCorrelation":
                            np.mean(
                                pairwise_corrs
                            ),

                        "MedianNetworkCorrelation":
                            np.median(
                                pairwise_corrs
                            ),

                        "MinNetworkCorrelation":
                            np.min(
                                pairwise_corrs
                            ),

                        "MaxNetworkCorrelation":
                            np.max(
                                pairwise_corrs
                            ),

                        "BestConnectedCell":
                            best_cell_row["Cell"],

                        "BestCellCorrelation":
                            best_cell_row["MeanCorrelation"],

                        "WorstConnectedCell":
                            worst_cell_row["Cell"],

                        "WorstCellCorrelation":
                            worst_cell_row["MeanCorrelation"]
                    }
                ]
            )

        return {
            "renorm_df": renorm_df,
            "correlation_matrix": corr_matrix,
            "cell_summary": cell_summary,
            "correlation_distribution": correlation_distribution,
            "network_summary": network_summary
        }

