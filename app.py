import streamlit as st
import pandas as pd
import graphviz as gv

# Mock data
data = {
    'Level': ['CNF', 'Super', 'Distributor', 'RSM', 'ASM', 
              'CNF', 'Super', 'Distributor', 'RSM', 'ASM'],
    'Entity': ['CNF-01', 'Super-001', 'Distributor-A', 'RSM-101', 'ASM-001', 
               'CNF-02', 'Super-002', 'Distributor-B', 'RSM-102', 'ASM-002'],
    'Employee Name': ['John Smith', 'John Smith', 'John Smith', 'John Smith', 'John Smith', 
                      'Jane Doe', 'Jane Doe', 'Jane Doe', 'Jane Doe', 'Jane Doe'],
    'Sales': [120000, 120000, 120000, 120000, 120000,
              150000, 150000, 150000, 150000, 150000],
    'Salary': [4000, 4000, 4000, 4000, 4000,
               4500, 4500, 4500, 4500, 4500],
    'Monthly Expenses': [500, 500, 500, 500, 500,
                         600, 600, 600, 600, 600]
}

# Create DataFrame
df = pd.DataFrame(data)

# Calculate Profit/Loss
df['Profit/Loss'] = df['Sales'] - (df['Salary'] + df['Monthly Expenses'])

# Aggregate sales for each level
aggregated_sales = df.groupby('Entity')['Sales'].sum().to_dict()

# Streamlit app
st.title("Employee Hierarchy Visualization with Sales at Each Point")

# Graphviz Digraph
dot = gv.Digraph()

# Create hierarchy in Graphviz
parent_map = {
    'Super': 'CNF',
    'Distributor': 'Super',
    'RSM': 'Distributor',
    'ASM': 'RSM'
}

for _, row in df.iterrows():
    entity = row['Entity']
    label = (f"{row['Employee Name']}\\n"
             f"Sales: ${aggregated_sales[entity]}\\n"
             f"Salary: ${row['Salary']}\\n"
             f"Expenses: ${row['Monthly Expenses']}\\n"
             f"Profit/Loss: ${row['Profit/Loss']}")
    dot.node(entity, label)
    
    # Add edges based on the hierarchy
    if row['Level'] == 'CNF':
        continue  # CNF has no parent
    parent_entity = df[df['Entity'] == f"{parent_map[row['Level']]}-{entity.split('-')[1]}"]['Entity'].values[0]
    dot.edge(parent_entity, entity)

st.graphviz_chart(dot)
