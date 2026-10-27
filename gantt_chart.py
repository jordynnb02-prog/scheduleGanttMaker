
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import re


# ---------------------------------------------------------
# FORMAT SECTION NAMES
# ---------------------------------------------------------

def formatSectionName(section):
    match = re.search(r"\((\d+)\)\s*$", section)

    if match:
        return f"Section {match.group(1)}"

    return section


# ---------------------------------------------------------
# CREATE GANTT CHART
# ---------------------------------------------------------

def createGanttChart(selectedGroups, expandedSections):

    sectionColors = [
        "#3B82F6",  # Blue
        "#8B5CF6",  # Purple
        "#F59E0B",  # Orange
        "#0D9488",  # Teal
        "#EC4899",  # Pink
        "#64748B"   # Gray
    ]

    # Store chart rows and their actual positions
    labels = []
    positions = []
    headerRows = []

    rowIndex = 0

    # Create the figure
    fig, ax = plt.subplots(figsize=(14, 8))

    for groupIndex, (section, tasks) in enumerate(selectedGroups.items()):

        color = sectionColors[groupIndex % len(sectionColors)]

        # Remove activities with missing or invalid dates
        validTasks = [
            task for task in tasks
            if isinstance(task.get("Start"), datetime)
            and isinstance(task.get("End"), datetime)
            and task["End"] >= task["Start"]
        ]

        validTasks = sorted(
            validTasks,
            key=lambda task: task["Start"]
        )

        if not validTasks:
            continue

        # Find section start and finish dates
        sectionStart = min(task["Start"] for task in validTasks)
        sectionEnd = max(task["End"] for task in validTasks)

        # -------------------------------------------------
        # SECTION HEADER
        # -------------------------------------------------

        labels.append(formatSectionName(section).upper())
        positions.append(rowIndex)
        headerRows.append(len(labels) - 1)

        ax.barh(
            rowIndex,
            width=mdates.date2num(sectionEnd) - mdates.date2num(sectionStart),
            left=mdates.date2num(sectionStart),
            height=0.85,
            color=color,
            alpha=0.35,
            edgecolor=color,
            linewidth=1
        )

        rowIndex += 1

        # -------------------------------------------------
        # INDIVIDUAL ACTIVITIES (ONLY WHEN EXPANDED)
        # -------------------------------------------------

        if section in expandedSections:

            for task in validTasks:

                labels.append("    " + task["Phase"].strip())
                positions.append(rowIndex)

                start = mdates.date2num(task["Start"])
                end = mdates.date2num(task["End"])

                ax.barh(
                    rowIndex,
                    width=end - start,
                    left=start,
                    height=0.55,
                    color=color
                )

                rowIndex += 1

        # Add spacing between major sections
        rowIndex += 0.8

    # ---------------------------------------------------------
    # AXIS LABELS
    # ---------------------------------------------------------

    ax.set_yticks(positions)
    ax.set_yticklabels(labels, fontsize=9)

    for index in headerRows:
        label = ax.get_yticklabels()[index]
        label.set_fontweight("bold")
        label.set_fontsize(11)

    ax.invert_yaxis()

    # ---------------------------------------------------------
    # DATE AXIS
    # ---------------------------------------------------------

    ax.xaxis_date()
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")

    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(
        mdates.ConciseDateFormatter(locator)
    )

    # ---------------------------------------------------------
    # TODAY LINE
    # ---------------------------------------------------------

    today = datetime.today()

    if positions:
        earliest = min(
            task["Start"]
            for tasks in selectedGroups.values()
            for task in tasks
            if isinstance(task.get("Start"), datetime)
        )

        latest = max(
            task["End"]
            for tasks in selectedGroups.values()
            for task in tasks
            if isinstance(task.get("End"), datetime)
        )

        if earliest <= today <= latest:
            ax.axvline(
                mdates.date2num(today),
                color="#DC2626",
                linestyle="--",
                linewidth=1.5,
                label="Today"
            )

            ax.legend(loc="upper right")

    # ---------------------------------------------------------
    # CHART FORMATTING
    # ---------------------------------------------------------

    # Adjust height based on visible rows, not all tasks
    chartHeight = min(20, max(5, rowIndex * 0.27))
    fig.set_size_inches(14, chartHeight)

    ax.grid(
        axis="x",
        linestyle="--",
        alpha=0.2
    )

    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    ax.tick_params(axis="y", length=0)

    fig.tight_layout()

    return fig
