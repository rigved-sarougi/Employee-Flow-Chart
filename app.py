import streamlit as st
import pandas as pd
import graphviz

# Load data
data = pd.read_csv('data.csv')

# Process numeric values from strings
data['Sales - After Closing'] = data['Sales - After Closing'].replace('[\$,]', '', regex=True).astype(float)
data['Salary'] = data['Salary'].replace('[\$,]', '', regex=True).astype(float)
data['Additional Monthly Expenses'] = data['Additional Monthly Expenses'].replace('[\$,]', '', regex=True).astype(float)

# Calculate monthly profit/loss
data['Total Monthly Expenses'] = data['Salary'] + data['Additional Monthly Expenses']
data['Profit/Loss'] = data['Sales - After Closing'] - data['Total Monthly Expenses']

# Filter options
employee_filter = st.sidebar.multiselect('Select Employees', data['Employee Name'].unique())
state_filter = st.sidebar.multiselect('Select States', data['Assigned State'].unique())

filtered_data = data.copy()
if employee_filter:
    filtered_data = filtered_data[filtered_data['Employee Name'].isin(employee_filter)]
if state_filter:
    filtered_data = filtered_data[filtered_data['Assigned State'].isin(state_filter)]

# Aggregation logic
if not filtered_data.empty:
    total_sales = filtered_data['Sales - After Closing'].sum()
    avg_salary = filtered_data['Salary'].mean()
    total_expenses = filtered_data['Additional Monthly Expenses'].sum()
    total_profit_loss = total_sales - (avg_salary + total_expenses)
else:
    total_sales = avg_salary = total_expenses = total_profit_loss = 0

# Display aggregated data
st.write(f"**Total Sales:** ${total_sales:,.2f}")
st.write(f"**Average Salary:** ${avg_salary:,.2f}")
st.write(f"**Total Additional Expenses:** ${total_expenses:,.2f}")
st.write(f"**Total Profit/Loss:** ${total_profit_loss:,.2f}")

# Graphviz chart
dot = graphviz.Digraph()

for _, row in filtered_data.iterrows():
    emp_details = (
        f"Name: {row['Employee Name']}\n"
        f"Sales: ${row['Sales - After Closing']:,.2f}\n"
        f"Salary: ${row['Salary']:,.2f}\n"
        f"Expenses: ${row['Additional Monthly Expenses']:,.2f}\n"
        f"Profit/Loss: ${row['Profit/Loss']:,.2f}"
    )
    dot.node(row['Employee Name'], emp_details)
    
    # Add relational hierarchy
    dot.edge(row['RSM'], row['ASM'], label="Reports to")
    dot.edge(row['Distributor'], row['RSM'], label="Distributor of")
    dot.edge(row['Super'], row['Distributor'], label="Supervised by")
    dot.edge(row['CNF'], row['Super'], label="Managed by")

st.graphviz_chart(dot)
