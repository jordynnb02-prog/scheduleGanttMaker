import re


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

    

# RETRIVE ALL ACTIVITIES FOR ONE SO NUMBER


# FILTER STAGES 
