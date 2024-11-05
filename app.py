import streamlit as st
import pandas as pd
import graphviz

# Load data
data = pd.read_csv('data.csv')

# Process numeric values from strings
data['Sales - After Closing'] = data['Sales - After Closing'].replace('[\$,]', '', regex=True).astype(float)
data['Salary'] = data['Salary'].replace('[\$,]', '', regex=True).astype(float)
data['Additional Monthly Expenses'] = data['Additional Monthly Expenses'].replace('[\$,]', '', regex=True).astype(float)

# Calculate total monthly expenses and profit/loss
data['Total Monthly Expenses'] = data['Salary'] + data['Additional Monthly Expenses']
data['Profit/Loss'] = data['Sales - After Closing'] - data['Total Monthly Expenses']

# Calculate average salary for each role
average_salary = data.groupby(['ASM', 'RSM', 'Distributor', 'Super', 'CNF'])['Salary'].mean().reset_index()

# Filter options
employee_filter = st.sidebar.multiselect('Select Employees', data['Employee Name'].unique())
state_filter = st.sidebar.multiselect('Select States', data['Assigned State'].unique())

filtered_data = data.copy()
if employee_filter:
    filtered_data = filtered_data[filtered_data['Employee Name'].isin(employee_filter)]
if state_filter:
    filtered_data = filtered_data[filtered_data['Assigned State'].isin(state_filter)]

# Display filtered data
st.dataframe(filtered_data)

# Graphviz chart
dot = graphviz.Digraph()

for _, row in filtered_data.iterrows():
    emp_details = (
        f"Name: {row['Employee Name']}\n"
        f"Sales: ${row['Sales - After Closing']}\n"
        f"Salary: ${row['Salary']}\n"
        f"Expenses: ${row['Additional Monthly Expenses']}\n"
        f"Profit/Loss: ${row['Profit/Loss']}"
    )
    dot.node(row['Employee Name'], emp_details)
    
    # Get average salary for roles
    average_salary_row = average_salary[(average_salary['ASM'] == row['ASM']) & 
                                         (average_salary['RSM'] == row['RSM']) & 
                                         (average_salary['Distributor'] == row['Distributor']) & 
                                         (average_salary['Super'] == row['Super']) & 
                                         (average_salary['CNF'] == row['CNF'])]
    
    avg_salary = average_salary_row['Salary'].values[0] if not average_salary_row.empty else 0
    
    # Add edges with average salary
    dot.node(row['CNF'], f"CNF: {row['CNF']}\nSales: ${row['Sales - After Closing']}\nAvg Salary: ${avg_salary}")
    dot.node(row['Super'], f"Super: {row['Super']}\nSales: ${row['Sales - After Closing']}\nAvg Salary: ${avg_salary}")
    dot.node(row['Distributor'], f"Distributor: {row['Distributor']}\nSales: ${row['Sales - After Closing']}\nAvg Salary: ${avg_salary}")
    dot.node(row['RSM'], f"RSM: {row['RSM']}\nSales: ${row['Sales - After Closing']}\nAvg Salary: ${avg_salary}")
    dot.node(row['ASM'], f"ASM: {row['ASM']}\nSales: ${row['Sales - After Closing']}\nAvg Salary: ${avg_salary}")

    # Add relational hierarchy
    dot.edge(row['RSM'], row['ASM'], label="Reports to")
    dot.edge(row['Distributor'], row['RSM'], label="Distributor of")
    dot.edge(row['Super'], row['Distributor'], label="Supervised by")
    dot.edge(row['CNF'], row['Super'], label="Managed by")

st.graphviz_chart(dot)
