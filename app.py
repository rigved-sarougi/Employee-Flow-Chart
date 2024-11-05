import pandas as pd
import streamlit as st
import graphviz as gv

# Load the data
data = pd.read_csv('Data.csv')

# Function to aggregate data by Employee Name
def aggregate_employee_data(employee_name, df):
    employee_data = df[df['Employee Name'] == employee_name]
    total_sales = employee_data['Sales - After Closing'].sum()
    salary = employee_data['Salary'].iloc[0]  # Assuming salary is consistent for the employee
    additional_expenses = employee_data['Additional Monthly Expenses'].iloc[0]  # Assuming expenses are consistent
    profit = total_sales - (salary + additional_expenses)
    return {
        "total_sales": total_sales,
        "salary": salary,
        "additional_expenses": additional_expenses,
        "profit": profit,
        "details": employee_data
    }

# Function to create a flowchart for an aggregated employee data
def create_aggregated_flowchart(employee_name, aggregated_data):
    flowchart = gv.Digraph(format="png")
    
    # Employee node with Salary, Expenses, and Profit/Loss
    flowchart.node("Employee", f"{employee_name}\nTotal Sales: {aggregated_data['total_sales']}\nSalary: {aggregated_data['salary']}\n"
                               f"Monthly Expenses: {aggregated_data['additional_expenses']}\nProfit: {aggregated_data['profit']}")

    # Add nodes for each unique hierarchy level with Sales details
    unique_roles = aggregated_data["details"].drop_duplicates(subset=['ASM', 'RSM', 'Distributor', 'Super', 'CNF'])
    
    for _, row in unique_roles.iterrows():
        flowchart.node("ASM", f"ASM: {row['ASM']}\nSales: {row['Sales - After Closing']}")
        flowchart.node("RSM", f"RSM: {row['RSM']}\nSales: {row['Sales - After Closing']}")
        flowchart.node("Distributor", f"Distributor: {row['Distributor']}\nSales: {row['Sales - After Closing']}")
        flowchart.node("Super", f"Super: {row['Super']}\nSales: {row['Sales - After Closing']}")
        flowchart.node("CNF", f"CNF: {row['CNF']}\nSales: {row['Sales - After Closing']}")
        
        # Add edges based on hierarchy
        flowchart.edge("Employee", "ASM")
        flowchart.edge("ASM", "RSM")
        flowchart.edge("RSM", "Distributor")
        flowchart.edge("Distributor", "Super")
        flowchart.edge("Super", "CNF")
    
    return flowchart

# Streamlit app for displaying and filtering employees
st.title("Employee Flowchart System with Aggregated Data")

# Filtering options
selected_employee = st.selectbox("Select Employee", data['Employee Name'].unique())
filtered_data = data[data['Employee Name'] == selected_employee]

# Aggregate data and create a flowchart for the selected employee
aggregated_data = aggregate_employee_data(selected_employee, data)
flowchart = create_aggregated_flowchart(selected_employee, aggregated_data)

# Display the flowchart
st.graphviz_chart(flowchart.source)
