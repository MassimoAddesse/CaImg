from pathlib import Path

import pandas as pd


def export_results(
        results: dict,
        output_path: str | Path
) -> Path:
    """
    Export CaImg Analyzer results into a single Excel workbook.

    Each type of extracted data is written to a separate worksheet.
    The ROI/cell identity is preserved wherever it is available.

    Parameters
    ----------
    results : dict
        Dictionary returned by CaImgPipeline.get_results().

    output_path : str or pathlib.Path
        Path of the Excel workbook to create.

    Returns
    -------
    pathlib.Path
        Path to the generated Excel workbook.
    """

    output_path = Path(output_path)

    if output_path.suffix.lower() != ".xlsx":
        output_path = output_path.with_suffix(".xlsx")

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with pd.ExcelWriter(
            output_path,
            engine="openpyxl"
    ) as writer:

        _write_dataframe(
            results.get("fluorescence"),
            writer,
            "Raw_Fluorescence"
        )

        _write_dataframe(
            results.get("f0"),
            writer,
            "F0"
        )

        _write_dataframe(
            results.get("dff"),
            writer,
            "DFF"
        )

        _write_detection_results(
            results.get("detection_results"),
            writer
        )

        _write_profiles(
            results.get("profiles"),
            writer
        )

        _write_analysis_results(
            results.get("analysis"),
            writer
        )

    return output_path


def _write_dataframe(
        data,
        writer,
        sheet_name: str
):
    """
    Write a pandas DataFrame to an Excel worksheet.

    Parameters
    ----------
    data : pandas.DataFrame or None
        Data to export.

    writer : pandas.ExcelWriter
        Active Excel writer.

    sheet_name : str
        Name of the worksheet.

    Returns
    -------
    None
        The dataframe is written to the workbook.
    """

    if data is None:
        return

    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            f"Expected a pandas DataFrame for '{sheet_name}', "
            f"got {type(data).__name__}."
        )

    data.to_excel(
        writer,
        sheet_name=sheet_name,
        index=True
    )


def _write_detection_results(
        detection_results,
        writer
):
    """
    Export detected events while preserving the ROI identifier.

    Parameters
    ----------
    detection_results : dict or None
        Dictionary whose keys identify ROIs and whose values
        contain the detected events for each ROI.

    writer : pandas.ExcelWriter
        Active Excel writer.

    Returns
    -------
    None
        Detection events are written to the Events worksheet.
    """

    if detection_results is None:
        return

    rows = []

    for roi, result in detection_results.items():

        events = getattr(
            result,
            "events",
            []
        )

        for event in events:

            if hasattr(event, "to_dict"):
                row = event.to_dict()
            else:
                row = {
                    "Event": getattr(
                        event,
                        "event_id",
                        None
                    ),
                    "Onset": getattr(
                        event,
                        "onset",
                        None
                    ),
                    "Peak": getattr(
                        event,
                        "peak",
                        None
                    ),
                    "Offset": getattr(
                        event,
                        "offset",
                        None
                    )
                }

            row["ROI"] = roi

            rows.append(row)

    if not rows:
        return

    pd.DataFrame(
        rows
    ).to_excel(
        writer,
        sheet_name="Events",
        index=False
    )


def _write_profiles(
        profiles,
        writer
):
    """
    Export event-based EventAnalysis results.

    Parameters
    ----------
    profiles : dict or list or None
        EventAnalysis results. A dictionary is expected to preserve
        ROI identifiers.

    writer : pandas.ExcelWriter
        Active Excel writer.

    Returns
    -------
    None
        Event metrics are written to the Event_Metrics worksheet.
    """

    if profiles is None:
        return

    rows = []

    if isinstance(profiles, dict):

        for roi, roi_profiles in profiles.items():

            for profiler in roi_profiles:

                if hasattr(profiler, "to_dict"):
                    row = profiler.to_dict()
                else:
                    row = dict(profiler)

                row["ROI"] = roi

                rows.append(row)

    elif isinstance(profiles, list):

        for profiler in profiles:

            if hasattr(profiler, "to_dict"):
                rows.append(
                    profiler.to_dict()
                )
            else:
                rows.append(
                    dict(profiler)
                )

    else:
        raise TypeError(
            "profiles must be a dictionary, list, or None."
        )

    if not rows:
        return

    pd.DataFrame(
        rows
    ).to_excel(
        writer,
        sheet_name="Event_Metrics",
        index=False
    )


def _write_analysis_results(
        analysis_results,
        writer
):
    """
    Export downstream cell and population analysis results.

    Parameters
    ----------
    analysis_results : dict or None
        Dictionary containing results generated by analysis_runner.py.

    writer : pandas.ExcelWriter
        Active Excel writer.

    Returns
    -------
    None
        Available analysis results are written to separate worksheets.
    """

    if analysis_results is None:
        return

    if not isinstance(
            analysis_results,
            dict
    ):
        raise TypeError(
            "analysis results must be a dictionary."
        )

    sheet_names = {
        "cell_metrics": "Cell_Metrics",
        "cell_metrics_df": "Cell_Metrics",
        "synchrony": "Synchrony",
        "correlation": "Correlation",
        "lagged_correlation": "Lagged_Correlation",
        "coactivity": "Coactivity",
        "event_overlap": "Event_Overlap",
        "population_activity": "Population_Activity",
        "activity_matrix": "Activity_Matrix",
    }

    for key, data in analysis_results.items():

        if data is None:
            continue

        sheet_name = sheet_names.get(
            key,
            key[:31]
        )

        if isinstance(
                data,
                pd.DataFrame
        ):

            data.to_excel(
                writer,
                sheet_name=sheet_name,
                index=True
            )

        elif isinstance(
                data,
                dict
        ):

            _write_dictionary_result(
                data,
                writer,
                sheet_name
            )


def _write_dictionary_result(
        data,
        writer,
        sheet_name: str
):
    """
    Convert a dictionary-based analysis result into a worksheet.

    Parameters
    ----------
    data : dict
        Dictionary containing analysis results.

    writer : pandas.ExcelWriter
        Active Excel writer.

    sheet_name : str
        Name of the worksheet.

    Returns
    -------
    None
        The dictionary is converted and written to Excel.
    """

    rows = []

    for key, value in data.items():

        if isinstance(
                value,
                pd.DataFrame
        ):

            dataframe = value.copy()

            if isinstance(
                    key,
                    tuple
            ):

                dataframe.insert(
                    0,
                    "ROI_A",
                    key[0]
                )

                dataframe.insert(
                    1,
                    "ROI_B",
                    key[1]
                )

            else:

                dataframe.insert(
                    0,
                    "ROI",
                    key
                )

            rows.append(
                dataframe
            )

        else:

            rows.append(
                {
                    "Key": str(key),
                    "Value": value
                }
            )

    if not rows:
        return

    if all(
            isinstance(row, pd.DataFrame)
            for row in rows
    ):

        output = pd.concat(
            rows,
            ignore_index=True
        )

    else:

        output = pd.DataFrame(
            rows
        )

    output.to_excel(
        writer,
        sheet_name=sheet_name[:31],
        index=False
    )
