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

    # Dictionary to store the last created node for each level in the hierarchy
    level_nodes = {}

    # Add nodes for each unique level and connect them hierarchically
    for level, details in aggregated_data["levels"].items():
        for role, sales in details.items():
            node_id = f"{level}_{role}"  # Create a unique node ID
            flowchart.node(node_id, f"{level}: {role}\nSales: {sales}")
            level_nodes[level] = node_id  # Store the last node for each level

    # Connect hierarchy levels in the order
    if 'ASM' in level_nodes:
        flowchart.edge("Employee", level_nodes['ASM'])
    if 'ASM' in level_nodes and 'RSM' in level_nodes:
        flowchart.edge(level_nodes['ASM'], level_nodes['RSM'])
    if 'RSM' in level_nodes and 'Distributor' in level_nodes:
        flowchart.edge(level_nodes['RSM'], level_nodes['Distributor'])
    if 'Distributor' in level_nodes and 'Super' in level_nodes:
        flowchart.edge(level_nodes['Distributor'], level_nodes['Super'])
    if 'Super' in level_nodes and 'CNF' in level_nodes:
        flowchart.edge(level_nodes['Super'], level_nodes['CNF'])

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
