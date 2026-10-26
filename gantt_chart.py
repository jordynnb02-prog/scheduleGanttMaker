import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def createGanttChart(projectTasks):
    chartHeight = max(6, len(projectTasks) * 0.4)
    fig, ax = plt.subplots(figsize=(12,chartHeight))

    for task in projectTasks:
        if task["Start"] is None or task["End"] is None:
            continue
        taskName = task["Stage"]
        start = mdates.date2num(task["Start"])
        end = mdates.date2num(task["End"])
        duration = end - start

        ax.barh(task["Phase"].strip(), width=duration, left=start)

        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

    return fig
