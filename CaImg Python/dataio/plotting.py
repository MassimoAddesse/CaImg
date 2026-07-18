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