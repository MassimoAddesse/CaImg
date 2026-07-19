import matplotlib.pyplot as plt


def plot_dff_traces(
        df,
        filename,
        title
):

    plt.figure(
        figsize=(15, 8)
    )

    for col in df.columns:

        plt.plot(
            df.index,
            df[col],
            linewidth=0.8
        )

    plt.title(title)

    plt.xlabel(
        "Frame"
    )

    plt.ylabel(
        "dF/F0"
    )

    plt.tight_layout()

    plt.savefig(
        filename,
        dpi=300
    )

    plt.close()

def plot_detected_events(
        dff_df,
        events,
        threshold,
        cell_name,
        filename
):
    
    trace = dff_df[
        cell_name
    ]

    plt.figure(
        figsize=(12, 4) 
    )

    plt.plot(
        trace.index,
        trace.values,
        color='blue',
        linewidth=1,
    )

    plt.axhline(
        y=threshold,
        color='green',
        linestyle='--',
        label='Threshold'
    )

    for start, end in events:
        plt.axvspan(
            start,
            end,
            color = 'red',
            alpha = 0.3
        )

    plt.legend()

    plt.savefig(
        filename,
        dpi=300
    )

    plt.close()