import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from graphviz import Digraph
import matplotlib.image as mpimg
from PIL import Image

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

# Function to create the flow chart
def create_flow_chart(employee_data, cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales, total_sales, total_expenses, avg_salary, target):
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

    # Employee node with detailed information
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

    return dot

# Generate the flow chart
flow_chart = create_flow_chart(filtered_data, cnf_sales, super_sales, distributor_sales, rsm_sales, asm_sales, total_sales, total_expenses, average_salary, employee_target)

# Save flowchart as PNG
flow_chart_path = '/mnt/data/flow_chart.png'
flow_chart.render(flow_chart_path, view=False)

# Create summary content as a text box
summary_content = f"""
Employee Name: {filtered_data['Employee Name'].iloc[0]}
Total Sales: ₹{total_sales:,.2f}
Target: ₹{employee_target:,.2f}
Total Expenses: ₹{total_expenses:,.2f}
Salary: ₹{average_salary:,.2f}
Profit: {'+' if profit > 0 else ''}₹{profit:,.2f} ({'Profit' if profit > 0 else 'Loss'})
Target Achievement: {target_percentage:.2f}%

Performance Status: {target_percentage:.2f}% Target Achievement
"""

# Create performance matrix as a table (color-coded)
fig, ax = plt.subplots(figsize=(6, 6))
ax.axis('off')

# Display performance status
performance_color = {
    'green': 'Above 90%',
    'yellow': 'Below 90%',
    'orange': 'Below 50%',
    'red': 'Below 30%'
}

table_data = [[performance_color[color], f"{target_percentage:.2f}%"]]
table = ax.table(cellText=table_data, colLabels=["Performance", "Percentage Achieved"], loc='center', cellLoc='center')

# Save this summary + flowchart as an image
combined_image_path = '/mnt/data/combined_image.png'

# Show the flowchart
img = mpimg.imread(flow_chart_path)
fig, ax = plt.subplots(figsize=(12, 10))

# Display flowchart and summary below
ax.imshow(img)
ax.text(0, 0, summary_content, fontsize=10, ha="left", va="bottom", color="black", bbox=dict(facecolor='white', alpha=0.7))

# Save combined image
plt.subplots_adjust(top=1.0, bottom=0.0)
plt.savefig(combined_image_path, dpi=300, bbox_inches="tight")
plt.close()

# Display the combined image for verification
st.image(combined_image_path)

# Provide the link to download the combined PNG
st.download_button(
    label="Download Performance Report",
    data=open(combined_image_path, "rb").read(),
    file_name="Employee_Performance_Report.png",
    mime="image/png"
)
