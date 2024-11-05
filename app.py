import streamlit as st
import pandas as pd
from graphviz import Digraph

# Load data from CSV
data = pd.read_csv('data.csv')

# Calculate profit status
data['Total Expenses'] = data['Salary'] + data['Additional Monthly Expenses']
data['Profit'] = data['Sales - After Closing'] - data['Total Expenses']
data['Profit Status'] = data['Profit'].apply(lambda x: 'Profit' if x > 0 else 'Loss')

# Streamlit app
st.title("Employee Hierarchy and Sales Overview")

# Create a filter for selecting employees
selected_employee = st.selectbox("Select Employee", data['Employee Name'].unique())
filtered_data = data[data['Employee Name'] == selected_employee]

# Grouping data to calculate total sales
cnf_sales = filtered_data.groupby('CNF')['Sales - After Closing'].sum().reset_index()
super_sales = filtered_data.groupby('Super')['Sales - After Closing'].sum().reset_index()
distributor_sales = filtered_data.groupby('Distributor')['Sales - After Closing'].sum().reset_index()
rsm_sales = filtered_data.groupby('RSM')['Sales - After Closing'].sum().reset_index()
asm_sales = filtered_data.groupby('ASM')['Sales - After Closing'].sum().reset_index()

# Calculate average salary for the selected employee
average_salary = filtered_data['Salary'].mean()

# Function to create the flow chart
def create_flow_chart(employee_data, cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales, avg_salary):
    dot = Digraph()
    
    # Adding CNF sales
    for index, row in cnf_sales.iterrows():
        cnf = row['CNF']
        total_cnf_sales = row['Sales - After Closing']
        dot.node(cnf, f'CNF: {cnf}\nSales: ${total_cnf_sales:,}', shape='box')
    
    # Adding Super sales
    for index, row in super_sales.iterrows():
        superv = row['Super']
        total_super_sales = row['Sales - After Closing']
        dot.node(superv, f'Super: {superv}\nSales: ${total_super_sales:,}', shape='box')
    
    # Adding Distributor sales
    for index, row in distributor_sales.iterrows():
        distributor = row['Distributor']
        total_distributor_sales = row['Sales - After Closing']
        dot.node(distributor, f'Distributor: {distributor}\nSales: ${total_distributor_sales:,}', shape='box')
    
    # Adding RSM sales
    for index, row in rsm_sales.iterrows():
        rsm = row['RSM']
        total_rsm_sales = row['Sales - After Closing']
        dot.node(rsm, f'RSM: {rsm}\nSales: ${total_rsm_sales:,}', shape='box')
    
    # Adding ASM sales
    for index, row in asm_sales.iterrows():
        asm = row['ASM']
        total_asm_sales = row['Sales - After Closing']
        dot.node(asm, f'ASM: {asm}\nSales: ${total_asm_sales:,}', shape='box')
    
    # Iterate over filtered data to create the detailed employee view
    for index, row in employee_data.iterrows():
        emp_name = row['Employee Name']
        sales = row['Sales - After Closing']
        expenses = row['Additional Monthly Expenses']
        profit = row['Profit']
        
        # Add the employee node with average salary
        dot.node(emp_name, f'Employee: {emp_name}\nSales: ${sales:,}\nSalary: ${avg_salary:,.2f}\nExpenses: ${expenses:,}\nProfit: ${profit:,}', shape='box', color='lightgreen' if profit > 0 else 'lightcoral')
        
        # Create edges based on CNF, Super, Distributor, RSM, ASM
        dot.edge(row['CNF'], row['Super'])
        dot.edge(row['Super'], row['Distributor'])
        dot.edge(row['Distributor'], row['RSM'])
        dot.edge(row['RSM'], row['ASM'])
        dot.edge(row['ASM'], emp_name)
    
    return dot

# Generate flow chart
flow_chart = create_flow_chart(filtered_data, cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales, average_salary)

# Render flow chart in Streamlit
st.graphviz_chart(flow_chart)
