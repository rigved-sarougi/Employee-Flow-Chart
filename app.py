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

# Create a Graphviz chart
dot = graphviz.Digraph()

# Calculate total sales for each hierarchical level
total_sales_by_role = data.groupby(['ASM', 'RSM', 'Distributor', 'Super', 'CNF'])['Sales - After Closing'].sum().reset_index()

# Create nodes for each employee and their respective hierarchical levels
for _, row in filtered_data.iterrows():
    # Employee details
    emp_details = (
        f"Name: {row['Employee Name']}\n"
        f"Sales: ${row['Sales - After Closing']}\n"
        f"Salary: ${row['Salary']}\n"
        f"Expenses: ${row['Additional Monthly Expenses']}\n"
        f"Profit/Loss: ${row['Profit/Loss']}"
    )
    
    # Create a node for the employee with complete details
    dot.node(row['Employee Name'], emp_details)
    
    # Get corresponding sales for each hierarchical level
    sales_row = total_sales_by_role[(total_sales_by_role['ASM'] == row['ASM']) &
                                     (total_sales_by_role['RSM'] == row['RSM']) &
                                     (total_sales_by_role['Distributor'] == row['Distributor']) &
                                     (total_sales_by_role['Super'] == row['Super']) &
                                     (total_sales_by_role['CNF'] == row['CNF'])]
    
    # Create nodes for CNF, Super, Distributor, RSM, and ASM with correct sales
    if not sales_row.empty:
        cnf_sales = sales_row['Sales - After Closing'].values[0]
        dot.node(row['CNF'], f"CNF: {row['CNF']}\nSales: ${cnf_sales}")
        
        super_sales = sales_row['Sales - After Closing'].values[0]
        dot.node(row['Super'], f"Super: {row['Super']}\nSales: ${super_sales}")
        
        distributor_sales = sales_row['Sales - After Closing'].values[0]
        dot.node(row['Distributor'], f"Distributor: {row['Distributor']}\nSales: ${distributor_sales}")
        
        rsm_sales = sales_row['Sales - After Closing'].values[0]
        dot.node(row['RSM'], f"RSM: {row['RSM']}\nSales: ${rsm_sales}")
        
        asm_sales = sales_row['Sales - After Closing'].values[0]
        dot.node(row['ASM'], f"ASM: {row['ASM']}\nSales: ${asm_sales}")
    
        # Add relational hierarchy
        dot.edge(row['RSM'], row['Employee Name'], label="Reports to")
        dot.edge(row['Distributor'], row['RSM'], label="Distributor of")
        dot.edge(row['Super'], row['Distributor'], label="Supervised by")
        dot.edge(row['CNF'], row['Super'], label="Managed by")

st.graphviz_chart(dot)
