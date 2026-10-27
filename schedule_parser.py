import re



def classifyProductionTask(taskName):
    name = taskName.strip().lower()

    if "assembly" in name or "assemble" in name or "cut, bend, punch" in name:
        return "Assembly"

    elif "install" in name:
        return "Installation"

    elif "wiring" in name or "wire" in name or "electrical" in name:
        return "Wiring"

    elif "qc" in name or "fat" in name or "punchlist" in name:
        return "Quality Control"

    elif "ship" in name or "inspection" in name:
        return "Shipping"

    return "Assembly"

def listAllSO(masterSchedule):
    allSOnums = []

    for row in masterSchedule:
        cell_value = row[1].value

        if isinstance(cell_value, str):
            so_match = re.match(r"SO\d+", cell_value.strip(), re.IGNORECASE)

            if so_match:
                so_number = so_match.group().upper()

                if so_number not in allSOnums:
                    allSOnums.append(so_number)

    return allSOnums

# READ AND ORGANIZE THE ENTIRE SCHEDULE WORKSHEET
def readMasterSchedule(masterSchedule):
    print("\n PROCESSING NEW FILE \n\n\n\n\n\n\n\n\n\n")
    so_numbers = listAllSO(masterSchedule)
    fullSchedule = {}
    for project in so_numbers:
        taskList = []
        wantedSO = False
        for row in masterSchedule:
            projectDates = {}
            if isinstance(row[1].value, str) and project in row[1].value:
                wantedSO = True
                stageName = row[1].value
            elif wantedSO and row[1].value and "SO" in row[1].value:
                wantedSO = False
            elif wantedSO and row[1].value:
                projectDates["Stage"] = stageName
                projectDates["Phase"] = row[1].value
                projectDates["Start"] = row[3].value
                projectDates["End"] = row[4].value
                taskList.append(projectDates)
        fullSchedule[project] = taskList
    return fullSchedule
    
# RETRIVE ALL ACTIVITIES FOR ONE SO NUMBER
def getSOactivities(fullSchedule, choosenSO):
    projectSchedule = fullSchedule[choosenSO]
    return projectSchedule

# FILTER STAGES 
def groupSchedule(projectTasks):
    groupedSchedule = {}
    stages = {task["Stage"].strip() for task in projectTasks}
    hasMultipleStages = len(stages) > 1

    for task in projectTasks:
        phase = task["Phase"].strip()
        stage = task["Stage"].strip()

        if phase in ("Elec. Drawings", "Mech. Drawings"):
            groupName = "Engineering / Drawings"
        elif phase in ("IFA", "Comments", "IFC"):
            groupName = "IFA Approval"
        elif phase  in ("Cutting", "Bending", "Welding", "Paint"):
            groupName = "Fabrication"
        else:
            if hasMultipleStages:
                groupName = stage
            else:
                groupName = "Production"

        groupedSchedule.setdefault(groupName, []).append(task)

    return groupedSchedule

def groupProductionTasks(tasks):
    subgroups = {}

    for task in tasks:
        category = classifyProductionTask(task["Phase"])

        subgroups.setdefault(category, []).append(task)

    return subgroups