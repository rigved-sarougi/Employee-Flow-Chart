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
st.title("🌟Biolume - Sales Hierarchy Flow Chart with Performance Matrix")
st.markdown("Analyze the performance, expenses, profit, and target achievement status of each employee in the sales hierarchy.")

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

# Grouping data for hierarchy levels
cnf_sales = filtered_data.groupby('CNF')['Sales - After Closing'].sum().reset_index()
super_sales = filtered_data.groupby('Super')['Sales - After Closing'].sum().reset_index()
distributor_sales = filtered_data.groupby('Distributor')['Sales - After Closing'].sum().reset_index()
rsm_sales = filtered_data.groupby('RSM')['Sales - After Closing'].sum().reset_index()
asm_sales = filtered_data.groupby('ASM')['Sales - After Closing'].sum().reset_index()

# Function to create the overall hierarchy flow chart
def create_hierarchy_flow_chart(employee_data, cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales, total_sales, total_expenses, avg_salary, target):
    dot = Digraph(format='png')
    dot.attr(rankdir='TB', size='12,10')
    
    node_style = {'shape': 'box', 'style': 'filled', 'fontname': 'Helvetica'}

    # Add CNF nodes
    for _, row in cnf_sales.iterrows():
        dot.node(row['CNF'], f'CNF: {row["CNF"]}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color='lightblue', **node_style)

    # Add Super nodes
    for _, row in super_sales.iterrows():
        dot.node(row['Super'], f'Super: {row["Super"]}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color='lightyellow', **node_style)

    # Add Distributor nodes
    for _, row in distributor_sales.iterrows():
        dot.node(row['Distributor'], f'Distributor: {row["Distributor"]}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color='lavender', **node_style)

    # Add RSM nodes
    for _, row in rsm_sales.iterrows():
        dot.node(row['RSM'], f'RSM: {row["RSM"]}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color='lightcoral', **node_style)

    # Add ASM nodes
    for _, row in asm_sales.iterrows():
        dot.node(row['ASM'], f'ASM: {row["ASM"]}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color='lightpink', **node_style)

    # Add the employee node with summarized data
    emp_name = employee_data['Employee Name'].iloc[0]
    dot.node(emp_name, f'Employee: {emp_name}\nTotal Sales: ₹{total_sales:,.2f}\nTarget: ₹{target:,.2f}\nSalary: ₹{avg_salary:,.2f}\nTotal Expenses: ₹{total_expenses:,.2f}\nProfit: ₹{profit:,.2f}',
             color='lightblue', **node_style)

    # Create edges for the hierarchy
    for _, row in employee_data.iterrows():
        dot.edge(row['CNF'], row['Super'])
        dot.edge(row['Super'], row['Distributor'])
        dot.edge(row['Distributor'], row['RSM'])
        dot.edge(row['RSM'], row['ASM'])
        dot.edge(row['ASM'], emp_name)

    return dot

# Generate the overall hierarchy flow chart
hierarchy_flow_chart = create_hierarchy_flow_chart(filtered_data, cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales, total_sales, total_expenses, average_salary, employee_target)

# Render hierarchy flow chart in Streamlit
st.subheader("📈 Overall Sales Hierarchy Flow Chart")
st.graphviz_chart(hierarchy_flow_chart)

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

# Separate summaries for each hierarchy level
st.markdown("### 🧩 Hierarchy Level Performance Summary")
def display_hierarchy_summary(level_data, level_name):
    for _, row in level_data.iterrows():
        st.markdown(f"""
        - **{level_name}:** `{row[level_name]}`
        - **Total Sales:** `₹{row['Sales - After Closing']:,.2f}`
        """)

st.markdown("#### CNF Level")
display_hierarchy_summary(cnf_sales, "CNF")

st.markdown("#### Super Level")
display_hierarchy_summary(super_sales, "Super")

st.markdown("#### Distributor Level")
display_hierarchy_summary(distributor_sales, "Distributor")

st.markdown("#### RSM Level")
display_hierarchy_summary(rsm_sales, "RSM")

st.markdown("#### ASM Level")
display_hierarchy_summary(asm_sales, "ASM")
