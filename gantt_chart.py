
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

today = datetime.today()


def createGanttChart(selectedGroups):

    # Count all rows, including section headers
    totalRows = sum(len(tasks) + 1 for tasks in selectedGroups.values())

    chartHeight = min(18, max(6, totalRows * 0.28))

    fig, ax = plt.subplots(figsize=(14, chartHeight))

    sectionColors = [
        "#3B82F6",  # Blue
        "#8B5CF6",  # Purple
        "#F59E0B",  # Orange
        "#0D9488",  # Teal
        "#EC4899",  # Pink
        "#64748B"   # Gray
    ]

    labels = []
    headerRows = []
    rowIndex = 0

    for groupIndex, (section, tasks) in enumerate(selectedGroups.items()):

        color = sectionColors[groupIndex % len(sectionColors)]

        # Keep only activities with valid dates
        validTasks = [
            task for task in tasks
            if task["Start"] is not None
            and task["End"] is not None
            and task["End"] >= task["Start"]
        ]
        validTasks = sorted(validTasks, key=lambda task: task["Start"])

        if not validTasks:
            continue

        # Find the overall date range of the section
        sectionStart = min(task["Start"] for task in validTasks)
        sectionEnd = max(task["End"] for task in validTasks)

        # Create the section header row
        labels.append(section.upper())
        headerRows.append(rowIndex)

        ax.barh(
            rowIndex,
            width=mdates.date2num(sectionEnd) - mdates.date2num(sectionStart),
            left=mdates.date2num(sectionStart),
            height=0.85,
            color=color,
            alpha=0.35,
            edgecolor=color
        )

        rowIndex += 1

        # Create individual activity rows
        for task in validTasks:

            labels.append("    " + task["Phase"].strip())

            start = mdates.date2num(task["Start"])
            end = mdates.date2num(task["End"])

            ax.barh(rowIndex, width=end - start, left=start, height=0.65, color=color)

            rowIndex += 1

    # Set activity names and section headings
    ax.set_yticks(range(rowIndex))
    ax.set_yticklabels(labels, fontsize=9)

    # Make section headings bold
    for index in headerRows:
        label = ax.get_yticklabels()[index]
        label.set_fontweight("bold")
        label.set_fontsize(12)
        rowIndex += 0.7

    # First activity at the top
    ax.invert_yaxis()
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")

    # Format the date axis
    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%b %d, %Y")
    )

    ax.axvline(mdates.date2num(today), color="#DC2626", linestyle="--", linewidth=1.5, label="Today")

    # Chart appearance
    ax.grid(axis="x", linestyle="--", alpha=0.2)
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    ax.tick_params(axis="y", length=0)

    fig.tight_layout()

    return fig
