import pandas as pd
import streamlit as st
import graphviz as gv

# Load the data
data = pd.read_csv('data.csv')

# Function to aggregate data by Employee Name with average salary and summed values
def aggregate_employee_data(employee_name, df):
    employee_data = df[df['Employee Name'] == employee_name]
    total_sales = employee_data['Sales - After Closing'].sum()
    average_salary = employee_data['Salary'].mean()  # Average salary for the employee
    total_expenses = employee_data['Additional Monthly Expenses'].sum()  # Sum of additional expenses
    profit = total_sales - (average_salary + total_expenses)
    
    # Get unique roles with aggregated sales for each level
    levels = {
        'ASM': employee_data.groupby('ASM')['Sales - After Closing'].sum().to_dict(),
        'RSM': employee_data.groupby('RSM')['Sales - After Closing'].sum().to_dict(),
        'Distributor': employee_data.groupby('Distributor')['Sales - After Closing'].sum().to_dict(),
        'Super': employee_data.groupby('Super')['Sales - After Closing'].sum().to_dict(),
        'CNF': employee_data.groupby('CNF')['Sales - After Closing'].sum().to_dict()
    }

    return {
        "total_sales": total_sales,
        "average_salary": average_salary,
        "total_expenses": total_expenses,
        "profit": profit,
        "levels": levels
    }

# Function to create a flowchart for an aggregated employee data
def create_aggregated_flowchart(employee_name, aggregated_data):
    flowchart = gv.Digraph(format="png")
    
    # Employee node with Average Salary, Summed Expenses, and Profit/Loss
    flowchart.node("Employee", f"{employee_name}\nTotal Sales: {aggregated_data['total_sales']}\nAverage Salary: {aggregated_data['average_salary']}\n"
                               f"Total Expenses: {aggregated_data['total_expenses']}\nProfit: {aggregated_data['profit']}")

    # Add nodes for each unique level and connect them hierarchically
    for level, details in aggregated_data["levels"].items():
        for role, sales in details.items():
            node_id = f"{level}_{role}"  # Create a unique node ID
            flowchart.node(node_id, f"{level}: {role}\nSales: {sales}")

    # Define hierarchy
    for asm in aggregated_data['levels']['ASM']:
        flowchart.edge("Employee", f"ASM_{asm}")
    for rsm in aggregated_data['levels']['RSM']:
        flowchart.edge(f"ASM_{asm}", f"RSM_{rsm}")
    for dist in aggregated_data['levels']['Distributor']:
        flowchart.edge(f"RSM_{rsm}", f"Distributor_{dist}")
    for sup in aggregated_data['levels']['Super']:
        flowchart.edge(f"Distributor_{dist}", f"Super_{sup}")
    for cnf in aggregated_data['levels']['CNF']:
        flowchart.edge(f"Super_{sup}", f"CNF_{cnf}")

    return flowchart

# Streamlit app for displaying and filtering employees
st.title("Employee Flowchart System with Aggregated Data")

# Filtering options
selected_employee = st.selectbox("Select Employee", data['Employee Name'].unique())

# Aggregate data and create a flowchart for the selected employee
aggregated_data = aggregate_employee_data(selected_employee, data)
flowchart = create_aggregated_flowchart(selected_employee, aggregated_data)

# Display the flowchart
st.graphviz_chart(flowchart.source)
