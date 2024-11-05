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

    # Create nodes and connect them hierarchically
    asm_nodes = []
    for asm, sales in aggregated_data['levels']['ASM'].items():
        asm_node = f"ASM_{asm}"
        flowchart.node(asm_node, f"ASM: {asm}\nSales: {sales}")
        flowchart.edge("Employee", asm_node)
        asm_nodes.append(asm_node)

    for rsm, sales in aggregated_data['levels']['RSM'].items():
        rsm_node = f"RSM_{rsm}"
        flowchart.node(rsm_node, f"RSM: {rsm}\nSales: {sales}")
        # Only connect RSMs to ASMs they are directly associated with
        for asm_node in asm_nodes:
            if asm_node.split('_')[1] in rsm:  # Assuming rsm contains asm info
                flowchart.edge(asm_node, rsm_node)

    for dist, sales in aggregated_data['levels']['Distributor'].items():
        dist_node = f"Distributor_{dist}"
        flowchart.node(dist_node, f"Distributor: {dist}\nSales: {sales}")
        # Only connect Distributors to RSMs they are directly associated with
        for rsm_node in aggregated_data['levels']['RSM']:
            if rsm_node.split('_')[1] in dist:  # Assuming dist contains rsm info
                flowchart.edge(rsm_node, dist_node)

    for sup, sales in aggregated_data['levels']['Super'].items():
        super_node = f"Super_{sup}"
        flowchart.node(super_node, f"Super: {sup}\nSales: {sales}")
        # Only connect Supers to Distributors they are directly associated with
        for dist_node in aggregated_data['levels']['Distributor']:
            if dist_node.split('_')[1] in sup:  # Assuming sup contains dist info
                flowchart.edge(dist_node, super_node)

    for cnf, sales in aggregated_data['levels']['CNF'].items():
        cnf_node = f"CNF_{cnf}"
        flowchart.node(cnf_node, f"CNF: {cnf}\nSales: {sales}")
        # Only connect CNFs to Supers they are directly associated with
        for super_node in aggregated_data['levels']['Super']:
            if super_node.split('_')[1] in cnf:  # Assuming cnf contains sup info
                flowchart.edge(super_node, cnf_node)

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
