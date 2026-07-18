import pandas as pd


def export_events(
        events,
        filename
):
    """
    Export Event objects to Excel.
    """

    rows = []

    for event in events:

        rows.append(
            {

                "Cell":
                    event.cell_id,

                "Start_Frame":
                    event.start_frame,

                "End_Frame":
                    event.end_frame,

                "Duration":
                    event.duration,

                "Peak":
                    event.peak,

                "Integral":
                    event.integral,

                "Rise_Time":
                    event.rise_time,

                "Decay_Time":
                    event.decay_time,

                "Rise_Speed":
                    event.rise_speed,

                "Decay_Speed":
                    event.decay_speed,

                "Event_STD":
                    event.event_std
            }
        )

    df = pd.DataFrame(
        rows
    )

    df.to_excel(
        filename,
        index=False
    )