# READ ALL SO NUMBERS FROM MASTER SCHEDULE
def listAllSO(masterScehdule):
    allSOnums = []
    for row in masterScehdule:
        if row[1].value is not None and "SO" in row[1].value and row[1].value not in allSOnums:
            allSOnums.append(row[1].value)
    return allSOnums

# READ AND ORGANIZE THE ENTIRE SCHEDULE WORKSHEET

    

# RETRIVE ALL ACTIVITIES FOR ONE SO NUMBER


# FILTER STAGES 
