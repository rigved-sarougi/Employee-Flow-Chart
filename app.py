import streamlit as st
import pandas as pd
from graphviz import Digraph

# Load data from CSV
data = pd.read_csv('data.csv')

# Calculate total expenses and profit status
data['Total Expenses'] = data['Salary'] + data['Additional Monthly Expenses']
data['Profit'] = data['Sales - After Closing'] - data['Total Expenses']
data['Profit Status'] = data['Profit'].apply(lambda x: 'Profit' if x > 0 else 'Loss')

# Aggregate sales at different levels
aggregate_sales = data.groupby(['CNF', 'Super', 'Distributor', 'RSM', 'ASM']).agg({'Sales - After Closing': 'sum'}).reset_index()

# Merge back to include sales in the original data
data = data.merge(aggregate_sales, on=['CNF', 'Super', 'Distributor', 'RSM', 'ASM'], suffixes=('', '_Total'))

# Streamlit app
st.title("Employee Hierarchy and Sales Overview")

# Create a filter for selecting employees
selected_employee = st.selectbox("Select Employee", data['Employee Name'].unique())
filtered_data = data[data['Employee Name'] == selected_employee]

# Function to create the flow chart
def create_flow_chart(employee_data):
    dot = Digraph()
    
    # Aggregate sales for each level
    for index, row in employee_data.iterrows():
        cnf = row['CNF']
        superv = row['Super']
        distributor = row['Distributor']
        rsm = row['RSM']
        asm = row['ASM']
        emp_name = row['Employee Name']
        sales_total = row['Sales - After Closing_Total']  # Total sales for the level
        salary = row['Salary']
        expenses = row['Additional Monthly Expenses']
        profit = row['Profit']
        
        # Add nodes for CNF, Super, Distributor, RSM, ASM, Employee
        dot.node(cnf, f'CNF: {cnf}\nSales: ${sales_total:,}', shape='box')
        dot.node(superv, f'Super: {superv}\nSales: ${sales_total:,}', shape='box')
        dot.node(distributor, f'Distributor: {distributor}\nSales: ${sales_total:,}', shape='box')
        dot.node(rsm, f'RSM: {rsm}\nSales: ${sales_total:,}', shape='box')
        dot.node(asm, f'ASM: {asm}\nSales: ${sales_total:,}', shape='box')
        dot.node(emp_name, f'Employee: {emp_name}\nSales: ${sales_total:,}\nSalary: ${salary:,}\nExpenses: ${expenses:,}\nProfit: ${profit:,}', shape='box', color='lightgreen' if profit > 0 else 'lightcoral')
        
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
