import streamlit as st
import pandas as pd
from graphviz import Digraph
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

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

# Function to create flow chart for a specific employee
def create_employee_flow_chart(employee_data, cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales, total_sales, total_expenses, avg_salary, target):
    dot = Digraph(format='png')
    dot.attr(rankdir='TB', size='12,10')
    
    node_style = {'shape': 'box', 'style': 'filled', 'fontname': 'Helvetica'}

    # Add CNF, Super, Distributor, RSM, and ASM sales nodes
    for level, sales, color in [
        ('CNF', cnf_sales, 'lightblue'),
        ('Super', super_sales, 'lightyellow'),
        ('Distributor', distributor_sales, 'lavender'),
        ('RSM', rsm_sales, 'lightcoral'),
        ('ASM', asm_sales, 'lightpink')
    ]:
        for _, row in sales.iterrows():
            dot.node(row[level], f'{level}: {row[level]}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color=color, **node_style)

    # Add employee node with details
    emp_name = employee_data['Employee Name'].iloc[0]
    dot.node(emp_name, f'Employee: {emp_name}\nTotal Sales: ₹{total_sales:,.2f}\nTarget: ₹{target:,.2f}\nSalary: ₹{avg_salary:,.2f}\nTotal Expenses: ₹{total_expenses:,.2f}\nProfit: ₹{profit:,.2f}',
             color='lightblue', **node_style)

    # Hierarchical edges
    for _, row in employee_data.iterrows():
        dot.edge(row['CNF'], row['Super'])
        dot.edge(row['Super'], row['Distributor'])
        dot.edge(row['Distributor'], row['RSM'])
        dot.edge(row['RSM'], row['ASM'])
        dot.edge(row['ASM'], emp_name)

    # Save the flowchart to a file
    file_path = "/tmp/employee_flowchart.png"
    dot.render(file_path)
    return file_path

# Generate the employee-specific flow chart
employee_flowchart_path = create_employee_flow_chart(filtered_data, cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales, total_sales, total_expenses, average_salary, employee_target)

# Function to create overall flowchart
def create_overall_flow_chart(data):
    dot = Digraph(format='png')
    dot.attr(rankdir='TB', size='12,10')

    node_style = {'shape': 'box', 'style': 'filled', 'fontname': 'Helvetica'}

    # Get unique CNF, Super, Distributor, RSM, ASM, Employee levels
    cnf_sales = data.groupby('CNF')['Sales - After Closing'].sum().reset_index()
    super_sales = data.groupby('Super')['Sales - After Closing'].sum().reset_index()
    distributor_sales = data.groupby('Distributor')['Sales - After Closing'].sum().reset_index()
    rsm_sales = data.groupby('RSM')['Sales - After Closing'].sum().reset_index()
    asm_sales = data.groupby('ASM')['Sales - After Closing'].sum().reset_index()

    # Add CNF, Super, Distributor, RSM, and ASM sales nodes
    for level, sales, color in [
        ('CNF', cnf_sales, 'lightblue'),
        ('Super', super_sales, 'lightyellow'),
        ('Distributor', distributor_sales, 'lavender'),
        ('RSM', rsm_sales, 'lightcoral'),
        ('ASM', asm_sales, 'lightpink')
    ]:
        for _, row in sales.iterrows():
            dot.node(row[level], f'{level}: {row[level]}\nSales: ₹{row["Sales - After Closing"]:,.2f}', color=color, **node_style)

    # Hierarchical edges
    for _, row in data.iterrows():
        dot.edge(row['CNF'], row['Super'])
        dot.edge(row['Super'], row['Distributor'])
        dot.edge(row['Distributor'], row['RSM'])
        dot.edge(row['RSM'], row['ASM'])
        dot.edge(row['ASM'], row['Employee Name'])

    # Save the flowchart to a file
    file_path = "/tmp/overall_flowchart.png"
    dot.render(file_path)
    return file_path

# Generate the overall flow chart
overall_flowchart_path = create_overall_flow_chart(data)

# Function to create PDF
def create_pdf(employee_flowchart_path, overall_flowchart_path, selected_employee, target_percentage, total_sales, employee_target, total_expenses, average_salary, profit):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    
    # Add Employee Flowchart
    c.drawImage(employee_flowchart_path, 50, 400, width=500, height=300)
    
    # Add Overall Flowchart
    c.drawImage(overall_flowchart_path, 50, 50, width=500, height=300)
    
    # Add Employee Performance Summary
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 700, f"Employee Name: {selected_employee}")
    c.drawString(50, 680, f"Target Achievement: {target_percentage:.2f}%")
    c.drawString(50, 660, f"Total Sales: ₹{total_sales:,.2f}")
    c.drawString(50, 640, f"Employee Target: ₹{employee_target:,.2f}")
    c.drawString(50, 620, f"Total Expenses: ₹{total_expenses:,.2f}")
    c.drawString(50, 600, f"Salary: ₹{average_salary:,.2f}")
    c.drawString(50, 580, f"Profit: ₹{profit:,.2f}")
    
    # Save PDF
    c.save()
    packet.seek(0)
    return packet

# Generate PDF
pdf_data = create_pdf(employee_flowchart_path, overall_flowchart_path, selected_employee, target_percentage, total_sales, employee_target, total_expenses, average_salary, profit)

# Provide download button for PDF
st.download_button(
    label="Download Sales Performance Report as PDF",
    data=pdf_data,
    file_name="employee_sales_performance_report.pdf",
    mime="application/pdf"
)
