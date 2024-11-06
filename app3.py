import streamlit as st
import pandas as pd
from graphviz import Digraph
from PIL import Image

# Load data from CSV
data = pd.read_csv('data.csv')

# Calculate profit status
data['Total Expenses'] = data['Salary'] + data['Additional Monthly Expenses']
data['Profit'] = data['Sales - After Closing'] - data['Total Expenses']
data['Profit Status'] = data['Profit'].apply(lambda x: 'Profit' if x > 0 else 'Loss')

# Streamlit app
st.title("Employee Sales Report")
st.markdown("### Overview of Employee Performance and Sales")

# Create a filter for selecting employees
selected_employee = st.selectbox("Select Employee", data['Employee Name'].unique())
filtered_data = data[data['Employee Name'] == selected_employee]

# Grouping data to calculate total sales and expenses
total_sales = filtered_data['Sales - After Closing'].sum()
total_expenses = filtered_data['Additional Monthly Expenses'].sum()
average_salary = filtered_data['Salary'].mean()

# Calculate profit after grouping
profit = total_sales - total_expenses

# Grouping data to calculate total sales for hierarchy levels
cnf_sales = filtered_data.groupby('CNF')['Sales - After Closing'].sum().reset_index()
super_sales = filtered_data.groupby('Super')['Sales - After Closing'].sum().reset_index()
distributor_sales = filtered_data.groupby('Distributor')['Sales - After Closing'].sum().reset_index()
rsm_sales = filtered_data.groupby('RSM')['Sales - After Closing'].sum().reset_index()
asm_sales = filtered_data.groupby('ASM')['Sales - After Closing'].sum().reset_index()

# Function to create the flow chart
def create_flow_chart(employee_data, cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales, total_sales, total_expenses, avg_salary):
    dot = Digraph(format='pdf')
    dot.attr(rankdir='TB', size='10,8')

    # Common node style without fillcolor
    node_style = {
        'style': 'filled',
        'fontname': 'Arial',
        'shape': 'box',
        'color': 'blue'
    }

    # Adding CNF sales
    for index, row in cnf_sales.iterrows():
        cnf = row['CNF']
        total_cnf_sales = row['Sales - After Closing']
        dot.node(cnf, f'CNF: {cnf}\nSales: ₹{total_cnf_sales:,.2f}', **node_style, fillcolor='lightblue')

    # Adding Super sales
    for index, row in super_sales.iterrows():
        superv = row['Super']
        total_super_sales = row['Sales - After Closing']
        dot.node(superv, f'Super: {superv}\nSales: ₹{total_super_sales:,.2f}', **node_style, fillcolor='lightyellow')

    # Adding Distributor sales
    for index, row in distributor_sales.iterrows():
        distributor = row['Distributor']
        total_distributor_sales = row['Sales - After Closing']
        dot.node(distributor, f'Distributor: {distributor}\nSales: ₹{total_distributor_sales:,.2f}', **node_style, fillcolor='lightgreen')

    # Adding RSM sales
    for index, row in rsm_sales.iterrows():
        rsm = row['RSM']
        total_rsm_sales = row['Sales - After Closing']
        dot.node(rsm, f'RSM: {rsm}\nSales: ₹{total_rsm_sales:,.2f}', **node_style, fillcolor='lightcoral')

    # Adding ASM sales
    for index, row in asm_sales.iterrows():
        asm = row['ASM']
        total_asm_sales = row['Sales - After Closing']
        dot.node(asm, f'ASM: {asm}\nSales: ₹{total_asm_sales:,.2f}', **node_style, fillcolor='lightpink')

    # Add the employee node with total sales, total expenses, and average salary
    emp_name = employee_data['Employee Name'].iloc[0]
    emp_color = 'lightgreen' if profit > 0 else 'lightcoral'
    dot.node(emp_name, f'Employee: {emp_name}\nTotal Sales: ₹{total_sales:,.2f}\nSalary: ₹{avg_salary:,.2f}\nTotal Expenses: ₹{total_expenses:,.2f}\nProfit: ₹{profit:,.2f}', 
             style='filled', fontname='Arial', shape='box', color='blue', fillcolor=emp_color)

    # Create edges based on CNF, Super, Distributor, RSM, ASM
    for index, row in employee_data.iterrows():
        dot.edge(row['CNF'], row['Super'])
        dot.edge(row['Super'], row['Distributor'])
        dot.edge(row['Distributor'], row['RSM'])
        dot.edge(row['RSM'], row['ASM'])
        dot.edge(row['ASM'], emp_name)

    dot.render('employee_hierarchy_flowchart')  # Save as PDF
    return 'employee_hierarchy_flowchart.pdf'

# Generate flow chart and load PDF
flow_chart_path = create_flow_chart(filtered_data, cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales, total_sales, total_expenses, average_salary)

# Display in Streamlit
st.subheader("📈 Sales Hierarchy Flow Chart")
st.markdown(f"### [Download the Flow Chart PDF](employee_hierarchy_flowchart.pdf)")

# Display summary report below the chart
st.markdown("### Summary of Employee Performance")
st.write(f"**Employee Name:** {filtered_data['Employee Name'].iloc[0]}")
st.write(f"**Total Sales:** ₹{total_sales:,.2f}")
st.write(f"**Total Expenses:** ₹{total_expenses:,.2f}")
st.write(f"**Average Salary:** ₹{average_salary:,.2f}")
st.write(f"**Profit:** ₹{profit:,.2f}")
