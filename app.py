import pandas as pd
import streamlit as st
import graphviz as gv

# Load the data
data = pd.read_csv('Test of Employee - Data - Sheet5.csv')

# Define function to create a flowchart for a given employee
def create_employee_flowchart(employee_data):
    flowchart = gv.Digraph(format="png")
    
    # Define nodes based on employee hierarchy
    flowchart.node("Employee", f"{employee_data['Employee Name']}\nCity: {employee_data['Assigned City']}\nState: {employee_data['Assigned State']}")
    flowchart.node("ASM", f"ASM: {employee_data['ASM']}\nSales: {employee_data['Sales - After Closing']}\nSalary: {employee_data['Salary']}")
    flowchart.node("RSM", f"RSM: {employee_data['RSM']}")
    flowchart.node("Distributor", f"Distributor: {employee_data['Distributor']}\nExpenses: {employee_data['Additional Monthly Expenses']}")
    flowchart.node("Super", f"Super: {employee_data['Super']}")
    flowchart.node("CNF", f"CNF: {employee_data['CNF']}")
    
    # Define edges
    flowchart.edge("Employee", "ASM")
    flowchart.edge("ASM", "RSM")
    flowchart.edge("RSM", "Distributor")
    flowchart.edge("Distributor", "Super")
    flowchart.edge("Super", "CNF")
    
    return flowchart

# Streamlit app for displaying and filtering employees
st.title("Employee Flowchart System")

# Filtering options
selected_employee = st.selectbox("Select Employee", ["All"] + list(data['Employee Name'].unique()))
selected_city = st.selectbox("Select City", ["All"] + list(data['Assigned City'].unique()))
sales_range = st.slider("Sales Range", int(data['Sales - After Closing'].min()), int(data['Sales - After Closing'].max()), (int(data['Sales - After Closing'].min()), int(data['Sales - After Closing'].max())))

# Filter data based on user selection
filtered_data = data.copy()
if selected_employee != "All":
    filtered_data = filtered_data[filtered_data['Employee Name'] == selected_employee]
if selected_city != "All":
    filtered_data = filtered_data[filtered_data['Assigned City'] == selected_city]
filtered_data = filtered_data[(filtered_data['Sales - After Closing'] >= sales_range[0]) & (filtered_data['Sales - After Closing'] <= sales_range[1])]

# Generate flowchart for each filtered employee
for _, employee_data in filtered_data.iterrows():
    flowchart = create_employee_flowchart(employee_data)
    st.graphviz_chart(flowchart.source)
