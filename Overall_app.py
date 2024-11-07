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
st.title("🌟Biolume - Overall Sales Hierarchy Flow Chart")
st.markdown("Analyze the sales hierarchy, performance, expenses, and profit for each employee in the organization.")

# Employee selection filter
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

# Grouping data for hierarchy levels (CNF, Super, Distributor, RSM, ASM)
cnf_sales = filtered_data.groupby('CNF')['Sales - After Closing'].sum().reset_index()
super_sales = filtered_data.groupby('Super')['Sales - After Closing'].sum().reset_index()
distributor_sales = filtered_data.groupby('Distributor')['Sales - After Closing'].sum().reset_index()
rsm_sales = filtered_data.groupby('RSM')['Sales - After Closing'].sum().reset_index()
asm_sales = filtered_data.groupby('ASM')['Sales - After Closing'].sum().reset_index()

# Function to create the flow chart with hierarchical levels
def create_hierarchy_flow_chart():
    dot = Digraph(format='png')
    dot.attr(rankdir='TB', size='12,10')
    
    node_style = {'shape': 'box', 'style': 'filled', 'fontname': 'Helvetica'}

    # Add CNF, Super, Distributor, RSM, ASM sales nodes
    for _, row in cnf_sales.iterrows():
        dot.node(row['CNF'], f'CNF: {row["CNF"]}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color='lightblue', **node_style)

    for _, row in super_sales.iterrows():
        dot.node(row['Super'], f'Super: {row["Super"]}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color='lightyellow', **node_style)

    for _, row in distributor_sales.iterrows():
        dot.node(row['Distributor'], f'Distributor: {row["Distributor"]}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color='lavender', **node_style)

    for _, row in rsm_sales.iterrows():
        dot.node(row['RSM'], f'RSM: {row["RSM"]}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color='lightcoral', **node_style)

    for _, row in asm_sales.iterrows():
        dot.node(row['ASM'], f'ASM: {row["ASM"]}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color='lightpink', **node_style)

    # Add employees below the ASM level
    for _, row in filtered_data.iterrows():
        dot.node(row['Employee Name'], f'Employee: {row["Employee Name"]}\nSales: ₹{row["Sales - After Closing"]:,.2f}\nTarget: ₹{row["Target"]:,.2f}', color='lightgreen', **node_style)

    # Add edges to create hierarchy (CNF -> Super -> Distributor -> RSM -> ASM -> Employee)
    for _, row in filtered_data.iterrows():
        dot.edge(row['CNF'], row['Super'])
        dot.edge(row['Super'], row['Distributor'])
        dot.edge(row['Distributor'], row['RSM'])
        dot.edge(row['RSM'], row['ASM'])
        dot.edge(row['ASM'], row['Employee Name'])

    return dot

# Generate and display the flow chart
flow_chart = create_hierarchy_flow_chart()
st.subheader("📈 Overall Sales Hierarchy Flow Chart")
st.graphviz_chart(flow_chart)

# Employee Performance Summary with Target Achievement
st.markdown("### 📊 Employee Performance Summary with Target Achievement")
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

