import streamlit as st
import pandas as pd
import numpy as np
from graphviz import Digraph
import matplotlib.pyplot as plt
from PIL import Image
import io

# Load the data (replace this with actual CSV data or database query)
data = pd.read_csv('data.csv')

# Calculate profit status
data['Total Expenses'] = data['Salary'] + data['Additional Monthly Expenses']
data['Profit'] = data['Sales - After Closing'] - data['Total Expenses']
data['Profit Status'] = data['Profit'].apply(lambda x: 'Profit' if x > 0 else 'Loss')

# Streamlit app setup
st.title("🌟Biolume - Employee Sales Flow Chart")
st.markdown("Analyze and visualize the performance, expenses, and profit status of each employee in the sales hierarchy.")

# Employee selection filter
selected_employee = st.selectbox("Select an Employee to View Details", data['Employee Name'].unique())
filtered_data = data[data['Employee Name'] == selected_employee]

# Grouping data to calculate total sales and expenses
total_sales = filtered_data['Sales - After Closing'].sum()
total_expenses = filtered_data['Additional Monthly Expenses'].sum()
average_salary = filtered_data['Salary'].mean()
employee_target = filtered_data['Target'].mean()
profit = total_sales - total_expenses
target_percentage = (total_sales / employee_target) * 100 if employee_target > 0 else 0

# Set color based on target achievement
if target_percentage >= 90:
    color = 'green'
elif target_percentage >= 50:
    color = 'yellow'
elif target_percentage >= 30:
    color = 'orange'
else:
    color = 'red'

# Function to create employee final report image
def create_employee_report(employee_data, total_sales, total_expenses, average_salary, target, profit, target_percentage, color):
    emp_name = employee_data['Employee Name'].iloc[0]
    report_text = f"""
    Employee Name: {emp_name}
    Total Sales: ₹{total_sales:,.2f}
    Target Sales: ₹{target:,.2f}
    Salary: ₹{average_salary:,.2f}
    Total Expenses: ₹{total_expenses:,.2f}
    Profit: ₹{profit:,.2f} ({'Profit' if profit > 0 else 'Loss'})
    Target Achievement: {target_percentage:.2f}%
    """

    fig, ax = plt.subplots(figsize=(6, 8))
    ax.axis('off')
    ax.text(0.5, 1.05, f"Employee Final Report: {emp_name}", fontsize=18, ha='center', fontweight='bold')
    ax.text(0.5, 0.85, report_text, fontsize=12, ha='center', va='top', wrap=True, bbox=dict(facecolor='lightgray', edgecolor='black', boxstyle='round,pad=0.3'))
    ax.barh([0], [target_percentage], color=color, edgecolor='black', height=0.3, alpha=0.8)
    ax.text(0.5, 0.6, f"Target Achievement: {target_percentage:.2f}%", fontsize=14, ha='center', va='center', color='white')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img = Image.open(buffer)
    return img

# Generate the final report image for the selected employee
employee_report_image = create_employee_report(filtered_data, total_sales, total_expenses, average_salary, employee_target, profit, target_percentage, color)

# Display the final report image
st.image(employee_report_image, caption=f"Final Report for {filtered_data['Employee Name'].iloc[0]}", use_column_width=True)

# Flow chart creation based on the employee data
def create_flow_chart(employee_data, total_sales, total_expenses, avg_salary, target):
    dot = Digraph(format='png')
    dot.attr(rankdir='TB', size='12,10')
    node_style = {'shape': 'box', 'style': 'filled', 'fontname': 'Helvetica'}

    # Adding employee node
    emp_name = employee_data['Employee Name'].iloc[0]
    dot.node(emp_name, f'Employee: {emp_name}\nTotal Sales: ₹{total_sales:,.2f}\nTarget: ₹{target:,.2f}\nSalary: ₹{avg_salary:,.2f}\nTotal Expenses: ₹{total_expenses:,.2f}\nProfit: ₹{profit:,.2f}', color='lightblue', **node_style)

    # Hierarchical nodes: CNF -> Super -> Distributor -> RSM -> ASM
    # Use your actual data for CNF, Super, Distributor, RSM, ASM
    cnf_sales = employee_data.groupby('CNF')['Sales - After Closing'].sum().reset_index()
    super_sales = employee_data.groupby('Super')['Sales - After Closing'].sum().reset_index()
    distributor_sales = employee_data.groupby('Distributor')['Sales - After Closing'].sum().reset_index()
    rsm_sales = employee_data.groupby('RSM')['Sales - After Closing'].sum().reset_index()
    asm_sales = employee_data.groupby('ASM')['Sales - After Closing'].sum().reset_index()

    # Add the hierarchical nodes
    for index, row in cnf_sales.iterrows():
        cnf = row['CNF']
        dot.node(cnf, f'CNF: {cnf}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color='lightblue', **node_style)
        dot.edge(cnf, emp_name)

    for index, row in super_sales.iterrows():
        superv = row['Super']
        dot.node(superv, f'Super: {superv}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color='lightyellow', **node_style)
        dot.edge(superv, emp_name)

    for index, row in distributor_sales.iterrows():
        distributor = row['Distributor']
        dot.node(distributor, f'Distributor: {distributor}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color='lavender', **node_style)
        dot.edge(distributor, emp_name)

    for index, row in rsm_sales.iterrows():
        rsm = row['RSM']
        dot.node(rsm, f'RSM: {rsm}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color='lightcoral', **node_style)
        dot.edge(rsm, emp_name)

    for index, row in asm_sales.iterrows():
        asm = row['ASM']
        dot.node(asm, f'ASM: {asm}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color='lightpink', **node_style)
        dot.edge(asm, emp_name)

    return dot

# Generate flow chart for the selected employee
flow_chart = create_flow_chart(filtered_data, total_sales, total_expenses, average_salary, employee_target)

# Display the flow chart in Streamlit
st.subheader("📈 Employee Sales Flow Chart")
st.graphviz_chart(flow_chart)

# Optional: You can also provide additional summary information like total sales, profit/loss, etc.
st.markdown(f"""
### 📊 Employee Performance Summary
- **Employee Name:** `{filtered_data['Employee Name'].iloc[0]}`
- **Total Sales:** `₹{total_sales:,.2f}`
- **Target:** `₹{employee_target:,.2f}`
- **Total Expenses:** `₹{total_expenses:,.2f}`
- **Salary:** `₹{average_salary:,.2f}`
- **Profit:** `{('+' if profit > 0 else '')}₹{profit:,.2f} ({'Profit' if profit > 0 else 'Loss'})`
""")

# Additional visualizations can be added based on your needs
