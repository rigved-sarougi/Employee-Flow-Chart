import pandas as pd
import streamlit as st
import graphviz as gv

# Load the data
data = pd.read_csv('data.csv')

# Function to aggregate data by Employee Name with average salary and summed values
def aggregate_employee_data(employee_name, df):
    employee_data = df[df['Employee Name'] == employee_name]
    total_sales = employee_data['Sales - After Closing'].sum()
    average_salary = employee_data['Salary'].mean()  # Average salary for the employee
    total_expenses = employee_data['Additional Monthly Expenses'].sum()  # Sum of additional expenses
    profit = total_sales - (average_salary + total_expenses)
    return {
        "total_sales": total_sales,
        "average_salary": average_salary,
        "total_expenses": total_expenses,
        "profit": profit,
        "details": employee_data
    }

# Function to create a flowchart for an aggregated employee data
def create_aggregated_flowchart(employee_name, aggregated_data):
    flowchart = gv.Digraph(format="png")
    
    # Employee node with Average Salary, Summed Expenses, and Profit/Loss
    flowchart.node("Employee", f"{employee_name}\nTotal Sales: {aggregated_data['total_sales']}\nAverage Salary: {aggregated_data['average_salary']}\n"
                               f"Total Expenses: {aggregated_data['total_expenses']}\nProfit: {aggregated_data['profit']}")

    # Add nodes for each unique hierarchy level with Sales details
    unique_roles = aggregated_data["details"].drop_duplicates(subset=['ASM', 'RSM', 'Distributor', 'Super', 'CNF'])
    
    for _, row in unique_roles.iterrows():
        flowchart.node("ASM", f"ASM: {row['ASM']}\nSales: {row['Sales - After Closing']}")
        flowchart.node("RSM", f"RSM: {row['RSM']}\nSales: {row['Sales - After Closing']}")
        flowchart.node("Distributor", f"Distributor: {row['Distributor']}\nSales: {row['Sales - After Closing']}")
        flowchart.node("Super", f"Super: {row['Super']}\nSales: {row['Sales - After Closing']}")
        flowchart.node("CNF", f"CNF: {row['CNF']}\nSales: {row['Sales - After Closing']}")
        
        # Add edges based on hierarchy
        flowchart.edge("Employee", "ASM")
        flowchart.edge("ASM", "RSM")
        flowchart.edge("RSM", "Distributor")
        flowchart.edge("Distributor", "Super")
        flowchart.edge("Super", "CNF")
    
    return flowchart

# Streamlit app for displaying and filtering employees
st.title("Employee Flowchart System with Aggregated Data")

# Filtering options
selected_employee = st.selectbox("Select Employee", data['Employee Name'].unique())
filtered_data = data[data['Employee Name'] == selected_employee]

# Aggregate data and create a flowchart for the selected employee
aggregated_data = aggregate_employee_data(selected_employee, data)
flowchart = create_aggregated_flowchart(selected_employee, aggregated_data)

# Display the flowchart
st.graphviz_chart(flowchart.source)
