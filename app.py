import streamlit as st
from openpyxl import load_workbook

from schedule_parser import listAllSO, getSOactivities

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


    st.text(getSOactivities(sheet, selectedSo))