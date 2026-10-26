import streamlit as st
from openpyxl import load_workbook

from schedule_parser import listAllSO, getSOactivities, groupSchedule
from gantt_chart import createGanttChart

st.title("Master Schedule Gantt Generator")

uploaded_file = st.file_uploader("Upload Master Schedule", type=["xlsm", "xlsx"])

if uploaded_file is not None:
    workbook = load_workbook(uploaded_file, data_only=True)
    st.success(f"Loaded: {uploaded_file.name}")
    st.success("Master Schedule loaded successfully!")

    if "Tasks" not in workbook.sheetnames:
        st.error("Tasks worksheet not found.")
        st.stop()

    sheet = workbook["Tasks"]

    so_nums = listAllSO(sheet)
    selectedSo = st.selectbox( "Select Service Order Number", sorted(so_nums), index=None, placeholder="Search for an SO")

    with st.spinner("Searching Master Schedule..."):
        projectSchedule = getSOactivities(sheet, selectedSo)

    if selectedSo is not None:

        grouped = groupSchedule(projectSchedule)
        selectedSections = []
        selectedTasks = []

        for section in grouped:
            if st.checkbox(section, value=True):
                selectedSections.append(section)
                selectedTasks.extend(grouped[section])
        if selectedTasks:
            fig = createGanttChart(selectedTasks)
            st.pyplot(fig)
        else:
            st.info("Select at least one section to display the Gantt chart.")