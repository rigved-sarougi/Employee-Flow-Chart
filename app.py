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

    return employee_data, {  # Return employee data along with aggregated values
        "total_sales": total_sales,
        "average_salary": average_salary,
        "total_expenses": total_expenses,
        "profit": profit,
        "levels": levels
    }

# Function to create a flowchart for an aggregated employee data
def create_aggregated_flowchart(employee_name, aggregated_data, employee_data):
    flowchart = gv.Digraph(format="png")
    
    # Employee node with Average Salary, Summed Expenses, and Profit/Loss
    flowchart.node("Employee", f"{employee_name}\nTotal Sales: {aggregated_data['total_sales']}\nAverage Salary: {aggregated_data['average_salary']}\n"
                               f"Total Expenses: {aggregated_data['total_expenses']}\nProfit: {aggregated_data['profit']}")

    # Create unique nodes and connect them hierarchically
    asm_nodes = {asm: f"ASM_{asm}" for asm in aggregated_data['levels']['ASM']}
    rsm_nodes = {rsm: f"RSM_{rsm}" for rsm in aggregated_data['levels']['RSM']}
    dist_nodes = {dist: f"Distributor_{dist}" for dist in aggregated_data['levels']['Distributor']}
    super_nodes = {sup: f"Super_{sup}" for sup in aggregated_data['levels']['Super']}
    cnf_nodes = {cnf: f"CNF_{cnf}" for cnf in aggregated_data['levels']['CNF']}

    # Connect Employee to each ASM node
    for asm, asm_id in asm_nodes.items():
        flowchart.node(asm_id, f"ASM: {asm}\nSales: {aggregated_data['levels']['ASM'][asm]}")
        flowchart.edge("Employee", asm_id)

        # Connect each ASM to their RSM
        for rsm in aggregated_data['levels']['RSM']:
            if rsm in employee_data['RSM'].values:
                rsm_id = rsm_nodes[rsm]
                flowchart.node(rsm_id, f"RSM: {rsm}\nSales: {aggregated_data['levels']['RSM'][rsm]}")
                flowchart.edge(asm_id, rsm_id)

                # Connect each RSM to their Distributor
                for dist in aggregated_data['levels']['Distributor']:
                    if dist in employee_data['Distributor'].values:
                        dist_id = dist_nodes[dist]
                        flowchart.node(dist_id, f"Distributor: {dist}\nSales: {aggregated_data['levels']['Distributor'][dist]}")
                        flowchart.edge(rsm_id, dist_id)

                        # Connect each Distributor to their Super
                        for sup in aggregated_data['levels']['Super']:
                            if sup in employee_data['Super'].values:
                                super_id = super_nodes[sup]
                                flowchart.node(super_id, f"Super: {sup}\nSales: {aggregated_data['levels']['Super'][sup]}")
                                flowchart.edge(dist_id, super_id)

                                # Connect each Super to their CNF
                                for cnf in aggregated_data['levels']['CNF']:
                                    if cnf in employee_data['CNF'].values:
                                        cnf_id = cnf_nodes[cnf]
                                        flowchart.node(cnf_id, f"CNF: {cnf}\nSales: {aggregated_data['levels']['CNF'][cnf]}")
                                        flowchart.edge(super_id, cnf_id)

    return flowchart

# Streamlit app for displaying and filtering employees
st.title("Employee Flowchart System with Aggregated Data")

# Filtering options
selected_employee = st.selectbox("Select Employee", data['Employee Name'].unique())

# Aggregate data and create a flowchart for the selected employee
employee_data, aggregated_data = aggregate_employee_data(selected_employee, data)
flowchart = create_aggregated_flowchart(selected_employee, aggregated_data, employee_data)

# Display the flowchart
st.graphviz_chart(flowchart.source)
