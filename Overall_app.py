import streamlit as st
import pandas as pd
from graphviz import Digraph

# Load data from CSV
data = pd.read_csv('data.csv')

# Calculate expenses, profit, and profit status
data['Total Expenses'] = data['Salary'] + data['Additional Monthly Expenses']
data['Profit'] = data['Sales - After Closing'] - data['Total Expenses']
data['Profit Status'] = data['Profit'].apply(lambda x: 'Profit' if x > 0 else 'Loss')

# Streamlit app setup
st.title("🌟Biolume - Sales Hierarchy Flow Chart with Overall Hierarchy")
st.markdown("Analyze the performance, expenses, profit, and target achievement status of each employee in the sales hierarchy.")

# Grouping data for hierarchy levels
cnf_sales = data.groupby('CNF')['Sales - After Closing'].sum().reset_index()
super_sales = data.groupby('Super')['Sales - After Closing'].sum().reset_index()
distributor_sales = data.groupby('Distributor')['Sales - After Closing'].sum().reset_index()
rsm_sales = data.groupby('RSM')['Sales - After Closing'].sum().reset_index()
asm_sales = data.groupby('ASM')['Sales - After Closing'].sum().reset_index()

# Function to create overall hierarchy flow chart under CNF
def create_overall_hierarchy_flow_chart(cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales):
    dot = Digraph(format='png')
    dot.attr(rankdir='TB', size='12,10')
    
    node_style = {'shape': 'box', 'style': 'filled', 'fontname': 'Helvetica'}

    # Adding CNF nodes
    for _, row in cnf_sales.iterrows():
        cnf = row['CNF']
        total_cnf_sales = row['Sales - After Closing']
        dot.node(cnf, f'CNF: {cnf}\nSales: ₹{total_cnf_sales:,.2f}', color='lightblue', **node_style)

    # Adding Super, Distributor, RSM, and ASM nodes
    for level, sales, color in [
        ('Super', super_sales, 'lightyellow'),
        ('Distributor', distributor_sales, 'lavender'),
        ('RSM', rsm_sales, 'lightcoral'),
        ('ASM', asm_sales, 'lightpink')
    ]:
        for _, row in sales.iterrows():
            dot.node(row[level], f'{level}: {row[level]}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color=color, **node_style)

    # Add the employee nodes (hierarchy-wise under each CNF)
    for _, row in data.iterrows():
        emp_name = row['Employee Name']
        total_sales = row['Sales - After Closing']
        dot.node(emp_name, f'Employee: {emp_name}\nSales: ₹{total_sales:,.2f}', color='lightgreen', **node_style)

    # Create edges for the hierarchy (CNF -> Super -> Distributor -> RSM -> ASM -> Employee)
    for _, row in data.iterrows():
        dot.edge(row['CNF'], row['Super'])
        dot.edge(row['Super'], row['Distributor'])
        dot.edge(row['Distributor'], row['RSM'])
        dot.edge(row['RSM'], row['ASM'])
        dot.edge(row['ASM'], row['Employee Name'])

    return dot

# Generate the overall hierarchy flow chart
overall_hierarchy_flow_chart = create_overall_hierarchy_flow_chart(cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales)

# Render overall hierarchy flow chart
st.subheader("📊 Overall Sales Hierarchy Flow Chart")
st.graphviz_chart(overall_hierarchy_flow_chart)

# Employee performance matrix filter
st.markdown("### 📊 Employee Performance Matrix")
selected_employee = st.selectbox("Select an Employee to View Details", data['Employee Name'].unique())
filtered_data = data[data['Employee Name'] == selected_employee]

# Calculate metrics for the selected employee
total_sales = filtered_data['Sales - After Closing'].sum()
total_expenses = filtered_data['Additional Monthly Expenses'].sum()
average_salary = filtered_data['Salary'].mean()
employee_target = filtered_data['Target'].mean()
profit = total_sales - total_expenses

# Calculate target achievement percentage and color code
target_percentage = (total_sales / employee_target) * 100 if employee_target > 0 else 0
if target_percentage >= 90:
    color = 'green'
elif target_percentage >= 50:
    color = 'yellow'
elif target_percentage >= 30:
    color = 'orange'
else:
    color = 'red'

# Performance summary for selected employee
st.markdown(f"""
- **Employee Name:** `{filtered_data['Employee Name'].iloc[0]}`
- **Total Sales:** `₹{total_sales:,.2f}`
- **Target:** `₹{employee_target:,.2f}`
- **Total Expenses:** `₹{total_expenses:,.2f}`
- **Salary:** `₹{average_salary:,.2f}`
- **Profit:** `{('+' if profit > 0 else '')}₹{profit:,.2f} ({'Profit' if profit > 0 else 'Loss'})`
- **Target Achievement:** `{target_percentage:.2f}%`
""")

# Color-coded performance indicator
st.markdown(f"<div style='background-color:{color};padding:10px;border-radius:5px;color:white;text-align:center;'>Target Achievement Status: {target_percentage:.2f}%</div>", unsafe_allow_html=True)

