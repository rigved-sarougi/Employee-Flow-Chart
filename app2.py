import pandas as pd
import streamlit as st
import pdfkit
import graphviz

# Load the data
data = pd.read_csv('data.csv')

# Sidebar filter for Employee Name
employee_name = st.sidebar.selectbox("Select Employee", data['Employee Name'].unique())

# Filter the data based on the selected employee
filtered_data = data[data['Employee Name'] == employee_name]

# Calculate totals and averages
total_sales = filtered_data['Sales - After Closing'].sum()
total_expenses = filtered_data['Additional Monthly Expenses'].sum()
average_salary = filtered_data['Salary'].mean()
profit = total_sales - total_expenses - average_salary

# Create Graphviz flowchart
dot = graphviz.Digraph()

# Add nodes and edges based on the employee's hierarchy
dot.node(employee_name, f'Employee: {employee_name}\nSales: ₹{total_sales:,.2f}\nSalary: ₹{average_salary:,.2f}\nExpenses: ₹{total_expenses:,.2f}\nProfit: ₹{profit:,.2f}', shape='box')

# Display the flowchart
st.graphviz_chart(dot)

# Display the summary
st.write("### Summary")
st.write(f"**Total Sales:** ₹{total_sales:,.2f}")
st.write(f"**Total Expenses:** ₹{total_expenses:,.2f}")
st.write(f"**Average Salary:** ₹{average_salary:,.2f}")
st.write(f"**Profit:** ₹{profit:,.2f}")

# PDF generation
if st.button("Generate PDF Report"):
    pdf_content = f"""
    <h1>Employee Sales Report</h1>
    <h2>Employee Name: {filtered_data['Employee Name'].iloc[0]}</h2>
    <h3>Summary</h3>
    <p><strong>Total Sales:</strong> ₹{total_sales:,.2f}</p>
    <p><strong>Total Expenses:</strong> ₹{total_expenses:,.2f}</p>
    <p><strong>Average Salary:</strong> ₹{average_salary:,.2f}</p>
    <p><strong>Profit:</strong> ₹{profit:,.2f}</p>
    """
    pdf_filename = f"{filtered_data['Employee Name'].iloc[0]}_sales_report.pdf"
    
    # Specify the path to the wkhtmltopdf executable
    config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')  # Update this path according to your installation

    # Generate PDF
    pdfkit.from_string(pdf_content, pdf_filename, configuration=config)
    
    st.success(f"PDF report generated: {pdf_filename}")
