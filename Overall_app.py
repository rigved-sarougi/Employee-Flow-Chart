import streamlit as st
import pandas as pd
from graphviz import Digraph

# Load data from CSV and add 'Target' column
data = pd.read_csv('data.csv')

# Calculate profit status
data['Total Expenses'] = data['Salary'] + data['Additional Monthly Expenses']
data['Profit'] = data['Sales - After Closing'] - data['Total Expenses']
data['Profit Status'] = data['Profit'].apply(lambda x: 'Profit' if x > 0 else 'Loss')

# Streamlit app
st.title("🌟 Biolume - Sales Hierarchy Flow Chart")
st.markdown("Analyze and visualize the performance, expenses, and profit status of each role in the sales hierarchy.")

# Role selection
role = st.selectbox("Select a Role to View Details", ['Employee', 'ASM', 'RSM', 'Distributor', 'Super', 'CNF'])

# Based on selected role, create a filter for specific individuals in that role
selected_person = st.selectbox(f"Select a {role} to View Details", data[role].unique())
filtered_data = data[data[role] == selected_person]

# Group data to calculate total sales and expenses
total_sales = filtered_data['Sales - After Closing'].sum()
total_expenses = filtered_data['Additional Monthly Expenses'].sum()
average_salary = filtered_data['Salary'].mean()
target = filtered_data['Target'].mean()  # Average target for the selected person
profit = total_sales - total_expenses

# Grouping data to calculate total sales for each level
cnf_sales = filtered_data.groupby('CNF')['Sales - After Closing'].sum().reset_index()
super_sales = filtered_data.groupby('Super')['Sales - After Closing'].sum().reset_index()
distributor_sales = filtered_data.groupby('Distributor')['Sales - After Closing'].sum().reset_index()
rsm_sales = filtered_data.groupby('RSM')['Sales - After Closing'].sum().reset_index()
asm_sales = filtered_data.groupby('ASM')['Sales - After Closing'].sum().reset_index()

# Function to create the flow chart
def create_flow_chart(filtered_data, cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales, total_sales, total_expenses, avg_salary, target):
    dot = Digraph(format='png')
    dot.attr(rankdir='TB', size='12,10')
    
    # Base style
    node_style = {'shape': 'box', 'style': 'filled', 'fontname': 'Helvetica'}

    # Adding CNF sales nodes
    for index, row in cnf_sales.iterrows():
        cnf = row['CNF']
        total_cnf_sales = row['Sales - After Closing']
        dot.node(cnf, f'CNF: {cnf}\nSales: ₹{total_cnf_sales:,.2f}', color='lightblue', **node_style)

    # Adding Super sales nodes
    for index, row in super_sales.iterrows():
        superv = row['Super']
        total_super_sales = row['Sales - After Closing']
        dot.node(superv, f'Super: {superv}\nSales: ₹{total_super_sales:,.2f}', color='lightyellow', **node_style)

    # Adding Distributor sales nodes with lavender color
    for index, row in distributor_sales.iterrows():
        distributor = row['Distributor']
        total_distributor_sales = row['Sales - After Closing']
        dot.node(distributor, f'Distributor: {distributor}\nSales: ₹{total_distributor_sales:,.2f}', color='lavender', **node_style)

    # Adding RSM sales nodes
    for index, row in rsm_sales.iterrows():
        rsm = row['RSM']
        total_rsm_sales = row['Sales - After Closing']
        dot.node(rsm, f'RSM: {rsm}\nSales: ₹{total_rsm_sales:,.2f}', color='lightcoral', **node_style)

    # Adding ASM sales nodes
    for index, row in asm_sales.iterrows():
        asm = row['ASM']
        total_asm_sales = row['Sales - After Closing']
        dot.node(asm, f'ASM: {asm}\nSales: ₹{total_asm_sales:,.2f}', color='lightpink', **node_style)

    # Add the selected role node with summarized data, including target
    color_map = {
        'Employee': 'lightblue',
        'ASM': 'lightpink',
        'RSM': 'lightcoral',
        'Distributor': 'lavender',
        'Super': 'lightyellow',
        'CNF': 'lightblue'
    }
    selected_color = color_map[role]
    dot.node(selected_person, f'{role}: {selected_person}\nTotal Sales: ₹{total_sales:,.2f}\nTarget: ₹{target:,.2f}\nSalary: ₹{avg_salary:,.2f}\nTotal Expenses: ₹{total_expenses:,.2f}\nProfit: ₹{profit:,.2f}',
             color=selected_color, **node_style)

    # Create edges for the hierarchy
    for index, row in filtered_data.iterrows():
        dot.edge(row['CNF'], row['Super'])
        dot.edge(row['Super'], row['Distributor'])
        dot.edge(row['Distributor'], row['RSM'])
        dot.edge(row['RSM'], row['ASM'])
        dot.edge(row['ASM'], row['Employee Name'])

    return dot

# Generate flow chart for the selected role
flow_chart = create_flow_chart(filtered_data, cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales, total_sales, total_expenses, average_salary, target)

# Render flow chart in Streamlit
st.subheader(f"📈 Sales Hierarchy Flow Chart for {role}: {selected_person}")
st.graphviz_chart(flow_chart)

# Display summary report below the chart
st.markdown("### 📊 Performance Summary")
st.markdown(f"""
- **{role} Name:** `{selected_person}`
- **Total Sales:** `₹{total_sales:,.2f}`
- **Target:** `₹{target:,.2f}`
- **Total Expenses:** `₹{total_expenses:,.2f}`
- **Salary:** `₹{average_salary:,.2f}`
- **Profit:** `{('+' if profit > 0 else '')}₹{profit:,.2f} ({'Profit' if profit > 0 else 'Loss'})`
""")

# Emphasize on profit or loss status
if profit > 0:
    st.success(f"This {role.lower()} is in profit! 🎉")
else:
    st.error(f"This {role.lower()} is currently operating at a loss. 📉")
