import streamlit as st
import pandas as pd
import graphviz

# Load data
data = pd.read_csv('data.csv')

# Process numeric values from strings
data['Sales - After Closing'] = data['Sales - After Closing'].replace('[\$,]', '', regex=True).astype(float)
data['Salary'] = data['Salary'].replace('[\$,]', '', regex=True).astype(float)
data['Additional Monthly Expenses'] = data['Additional Monthly Expenses'].replace('[\$,]', '', regex=True).astype(float)

# Calculate monthly expenses and profit/loss
data['Total Monthly Expenses'] = data['Salary'] + data['Additional Monthly Expenses']
data['Profit/Loss'] = data['Sales - After Closing'] - data['Total Monthly Expenses']

# Average salary by role
average_salaries = data.groupby(['ASM', 'RSM', 'Distributor', 'Super', 'CNF']).agg({
    'Salary': 'mean',
    'Sales - After Closing': 'sum'
}).reset_index()

# Filter options
employee_filter = st.sidebar.multiselect('Select Employees', data['Employee Name'].unique())
state_filter = st.sidebar.multiselect('Select States', data['Assigned State'].unique())

# Filtering data based on selections
filtered_data = data.copy()
if employee_filter:
    filtered_data = filtered_data[filtered_data['Employee Name'].isin(employee_filter)]
if state_filter:
    filtered_data = filtered_data[filtered_data['Assigned State'].isin(state_filter)]

# Display filtered data
st.dataframe(filtered_data)

# Graphviz chart
dot = graphviz.Digraph()

# Add nodes for each employee in the filtered data
for _, row in filtered_data.iterrows():
    emp_details = (
        f"Name: {row['Employee Name']}\n"
        f"Sales: ${row['Sales - After Closing']}\n"
        f"Salary: ${row['Salary']}\n"
        f"Expenses: ${row['Additional Monthly Expenses']}\n"
        f"Profit/Loss: ${row['Profit/Loss']}"
    )
    dot.node(row['Employee Name'], emp_details)

# Add hierarchy levels and average sales
for _, row in average_salaries.iterrows():
    # Average salary and total sales for each level
    avg_salary = row['Salary']
    total_sales = row['Sales - After Closing']

    # Adding nodes for each role level
    for role in ['CNF', 'Super', 'Distributor', 'RSM', 'ASM']:
        role_name = row[role]
        if role_name:
            role_details = (
                f"{role}: {role_name}\n"
                f"Average Salary: ${avg_salary:.2f}\n"
                f"Total Sales: ${total_sales:.2f}"
            )
            dot.node(role_name, role_details)

            # Adding edges to represent hierarchy
            if role == 'ASM':
                dot.edge(role_name, row['RSM'], label="Reports to")
            elif role == 'RSM':
                dot.edge(role_name, row['Distributor'], label="Distributor of")
            elif role == 'Distributor':
                dot.edge(role_name, row['Super'], label="Supervised by")
            elif role == 'Super':
                dot.edge(role_name, row['CNF'], label="Managed by")

st.graphviz_chart(dot)
