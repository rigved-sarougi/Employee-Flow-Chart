import streamlit as st
import pandas as pd
from graphviz import Digraph

# Load data from CSV
data = pd.read_csv('data.csv')

# Calculate total sales for each CNF, Super, Distributor, RSM, and ASM
total_sales = data.groupby(['CNF', 'Super', 'Distributor', 'RSM', 'ASM']).agg({
    'Sales - After Closing': 'sum',
    'Salary': 'mean',
    'Additional Monthly Expenses': 'sum'
}).reset_index()

# Merge with original data to get employee names
merged_data = data.merge(total_sales, on=['CNF', 'Super', 'Distributor', 'RSM', 'ASM'], suffixes=('', '_total'))

# Calculate profit status
merged_data['Total Expenses'] = merged_data['Salary_total'] + merged_data['Additional Monthly Expenses_total']
merged_data['Profit'] = merged_data['Sales - After Closing_total'] - merged_data['Total Expenses']
merged_data['Profit Status'] = merged_data['Profit'].apply(lambda x: 'Profit' if x > 0 else 'Loss')

# Streamlit app
st.title("Employee Hierarchy and Sales Overview")

# Create a filter for selecting employees
selected_employee = st.selectbox("Select Employee", data['Employee Name'].unique())
filtered_data = merged_data[merged_data['Employee Name'] == selected_employee]

# Function to create the flow chart
def create_flow_chart(employee_data):
    dot = Digraph()
    
    for index, row in employee_data.iterrows():
        cnf = row['CNF']
        superv = row['Super']
        distributor = row['Distributor']
        rsm = row['RSM']
        asm = row['ASM']
        emp_name = row['Employee Name']
        sales = row['Sales - After Closing_total']
        avg_salary = row['Salary_total']
        total_expenses = row['Additional Monthly Expenses_total']
        profit = row['Profit']
        
        # Add nodes for CNF, Super, Distributor, RSM, ASM, Employee
        dot.node(cnf, f'CNF: {cnf}\nSales: ${sales:,}', shape='box')
        dot.node(superv, f'Super: {superv}\nSales: ${sales:,}', shape='box')
        dot.node(distributor, f'Distributor: {distributor}\nSales: ${sales:,}', shape='box')
        dot.node(rsm, f'RSM: {rsm}\nSales: ${sales:,}', shape='box')
        dot.node(asm, f'ASM: {asm}\nSales: ${sales:,}', shape='box')
        dot.node(emp_name, f'Employee: {emp_name}\nSales: ${sales:,}\nAvg Salary: ${avg_salary:,}\nExpenses: ${total_expenses:,}\nProfit: ${profit:,}', shape='box', color='lightgreen' if profit > 0 else 'lightcoral')
        
        # Create edges
        dot.edge(cnf, superv)
        dot.edge(superv, distributor)
        dot.edge(distributor, rsm)
        dot.edge(rsm, asm)
        dot.edge(asm, emp_name)
    
    return dot

# Generate flow chart
flow_chart = create_flow_chart(filtered_data)

# Render flow chart in Streamlit
st.graphviz_chart(flow_chart)
