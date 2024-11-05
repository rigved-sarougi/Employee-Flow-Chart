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

# Grouping data to calculate total sales and average salary
cnf_sales = filtered_data.groupby('CNF')['Sales - After Closing'].sum().reset_index()
super_sales = filtered_data.groupby('Super')['Sales - After Closing'].sum().reset_index()

# Calculate average salary for the selected employee
average_salary = filtered_data['Salary'].mean()

# Function to create the flow chart
def create_flow_chart(employee_data, cnf_sales, super_sales, avg_salary):
    dot = Digraph()
    
    # Adding CNF and Super sales
    for index, row in cnf_sales.iterrows():
        cnf = row['CNF']
        total_cnf_sales = row['Sales - After Closing']
        dot.node(cnf, f'CNF: {cnf}\nSales: ${total_cnf_sales:,}', shape='box')
    
    for index, row in super_sales.iterrows():
        superv = row['Super']
        total_super_sales = row['Sales - After Closing']
        dot.node(superv, f'Super: {superv}\nSales: ${total_super_sales:,}', shape='box')
    
    # Iterate over filtered data to create the detailed employee view
    for index, row in employee_data.iterrows():
        emp_name = row['Employee Name']
        sales = row['Sales - After Closing']
        expenses = row['Additional Monthly Expenses']
        profit = row['Profit']

        # Add the employee node with average salary
        dot.node(emp_name, f'Employee: {emp_name}\nSales: ${sales:,}\nSalary: ${avg_salary:,.2f}\nExpenses: ${expenses:,}\nProfit: ${profit:,}', shape='box', color='lightgreen' if profit > 0 else 'lightcoral')
        
        # Create edges based on CNF and Super
        dot.edge(row['CNF'], row['Super'])
        dot.edge(row['Super'], emp_name)
    
    return dot

# Generate flow chart
flow_chart = create_flow_chart(filtered_data, cnf_sales, super_sales, average_salary)

# Render flow chart in Streamlit
st.graphviz_chart(flow_chart)
