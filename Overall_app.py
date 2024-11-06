import streamlit as st
import pandas as pd
from graphviz import Digraph

# Load data from CSV and add 'Target' column
data = pd.read_csv('data.csv')  # Default target value; modify as needed or adjust in your CSV

# Calculate profit status
data['Total Expenses'] = data['Salary'] + data['Additional Monthly Expenses']
data['Profit'] = data['Sales - After Closing'] - data['Total Expenses']
data['Profit Status'] = data['Profit'].apply(lambda x: 'Profit' if x > 0 else 'Loss')

# Streamlit app
st.title("🌟Biolume - Employee Sales Performance Dashboard")
st.markdown("Analyze and visualize the performance, expenses, and profit status of each employee in the sales hierarchy.")

# Create a filter for selecting employees
selected_employee = st.selectbox("Select an Employee to View Details", data['Employee Name'].unique())

# Filter data for the selected employee
filtered_data = data[data['Employee Name'] == selected_employee]

# Grouping data to calculate total sales and expenses
total_sales = filtered_data['Sales - After Closing'].sum()
total_expenses = filtered_data['Additional Monthly Expenses'].sum()
average_salary = filtered_data['Salary'].mean()
employee_target = filtered_data['Target'].mean()  # Average target for the selected employee

# Calculate profit
profit = total_sales - total_expenses

# Grouping data to calculate total sales for hierarchy levels
cnf_sales = data.groupby('CNF')['Sales - After Closing'].sum().reset_index()
super_sales = data.groupby('Super')['Sales - After Closing'].sum().reset_index()
distributor_sales = data.groupby('Distributor')['Sales - After Closing'].sum().reset_index()
rsm_sales = data.groupby('RSM')['Sales - After Closing'].sum().reset_index()
asm_sales = data.groupby('ASM')['Sales - After Closing'].sum().reset_index()

# Function to create the flow chart
def create_flow_chart(employee_data, cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales, total_sales, total_expenses, avg_salary, target):
    dot = Digraph(format='png')
    dot.attr(rankdir='TB', size='12,10')
    
    # Base style
    node_style = {'shape': 'box', 'style': 'filled', 'fontname': 'Helvetica'}

    # Adding CNF sales nodes
    for index, row in cnf_sales.iterrows():
        cnf = row['CNF']
        total_cnf_sales = row['Sales - After Closing']
        dot.node(cnf, f'CNF: {cnf}\nSales: ₹{total_cnf_sales:,.2f}', color='lightblue', **node_style)

    # Adding Super sales nodes
    for index, row in super_sales.iterrows():
        superv = row['Super']
        total_super_sales = row['Sales - After Closing']
        dot.node(superv, f'Super: {superv}\nSales: ₹{total_super_sales:,.2f}', color='lightyellow', **node_style)

    # Adding Distributor sales nodes with lavender color
    for index, row in distributor_sales.iterrows():
        distributor = row['Distributor']
        total_distributor_sales = row['Sales - After Closing']
        dot.node(distributor, f'Distributor: {distributor}\nSales: ₹{total_distributor_sales:,.2f}', color='lavender', **node_style)

    # Adding RSM sales nodes
    for index, row in rsm_sales.iterrows():
        rsm = row['RSM']
        total_rsm_sales = row['Sales - After Closing']
        dot.node(rsm, f'RSM: {rsm}\nSales: ₹{total_rsm_sales:,.2f}', color='lightcoral', **node_style)

    # Adding ASM sales nodes
    for index, row in asm_sales.iterrows():
        asm = row['ASM']
        total_asm_sales = row['Sales - After Closing']
        dot.node(asm, f'ASM: {asm}\nSales: ₹{total_asm_sales:,.2f}', color='lightpink', **node_style)

    # Add the employee node with summarized data, including target
    emp_name = employee_data['Employee Name'].iloc[0]
    emp_color = 'lightblue'  # Light blue for employee box
    dot.node(emp_name, f'Employee: {emp_name}\nTotal Sales: ₹{total_sales:,.2f}\nTarget: ₹{target:,.2f}\nSalary: ₹{avg_salary:,.2f}\nTotal Expenses: ₹{total_expenses:,.2f}\nProfit: ₹{profit:,.2f}',
             color=emp_color, **node_style)

    # Create edges for the hierarchy
    for index, row in employee_data.iterrows():
        dot.edge(row['CNF'], row['Super'])
        dot.edge(row['Super'], row['Distributor'])
        dot.edge(row['Distributor'], row['RSM'])
        dot.edge(row['RSM'], row['ASM'])
        dot.edge(row['ASM'], emp_name)

    return dot

# Default chart for the overall data
default_flow_chart = create_flow_chart(data, cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales, total_sales, total_expenses, average_salary, employee_target)

# Render flow chart in Streamlit
st.subheader("📈 Overall Sales Hierarchy Flow Chart")
st.graphviz_chart(default_flow_chart)

# If an employee is selected, generate the filtered chart
if selected_employee:
    flow_chart = create_flow_chart(filtered_data, cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales, total_sales, total_expenses, average_salary, employee_target)
    st.subheader(f"📈 Sales Hierarchy Flow Chart for {selected_employee}")
    st.graphviz_chart(flow_chart)

    # Display summary report below the chart
    st.markdown("### 📊 Employee Performance Summary")
    st.markdown(f"""
    - **Employee Name:** `{filtered_data['Employee Name'].iloc[0]}`
    - **Total Sales:** `₹{total_sales:,.2f}`
    - **Target:** `₹{employee_target:,.2f}`
    - **Total Expenses:** `₹{total_expenses:,.2f}`
    - **Salary:** `₹{average_salary:,.2f}`
    - **Profit:** `{('+' if profit > 0 else '')}₹{profit:,.2f} ({'Profit' if profit > 0 else 'Loss'})`
    """)

    # Emphasize on profit or loss status
    if profit > 0:
        st.success("This employee is in profit! 🎉")
    else:
        st.error("This employee is currently operating at a loss. 📉")
