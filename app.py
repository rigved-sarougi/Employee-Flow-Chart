import streamlit as st
import pandas as pd
from graphviz import Digraph

# Load data from CSV
data = pd.read_csv('data.csv')

# Calculate total expenses and profit status
data['Total Expenses'] = data['Salary'] + data['Additional Monthly Expenses']
data['Profit'] = data['Sales - After Closing'] - data['Total Expenses']
data['Profit Status'] = data['Profit'].apply(lambda x: 'Profit' if x > 0 else 'Loss')

# Function to create the flow chart
def create_flow_chart(data):
    dot = Digraph()
    
    # Group data by CNF and calculate total sales for CNF and Super
    cnf_group = data.groupby('CNF').agg({
        'Sales - After Closing': 'sum',
        'Salary': 'mean',  # Average salary for CNF
        'Additional Monthly Expenses': 'sum'  # Total expenses for CNF
    }).reset_index()
    
    for _, cnf_row in cnf_group.iterrows():
        cnf = cnf_row['CNF']
        cnf_sales = cnf_row['Sales - After Closing']
        cnf_salary = cnf_row['Salary']
        cnf_expenses = cnf_row['Additional Monthly Expenses']
        
        # Add CNF node
        dot.node(cnf, f'CNF: {cnf}\nTotal Sales: ${cnf_sales:,}\nAvg Salary: ${cnf_salary:,}\nTotal Expenses: ${cnf_expenses:,}', shape='box')
        
        # Get Super data for this CNF
        super_group = data[data['CNF'] == cnf].groupby('Super').agg({
            'Sales - After Closing': 'sum',
            'Salary': 'mean',  # Average salary for Super
            'Additional Monthly Expenses': 'sum'  # Total expenses for Super
        }).reset_index()

        for _, super_row in super_group.iterrows():
            superv = super_row['Super']
            super_sales = super_row['Sales - After Closing']
            super_salary = super_row['Salary']
            super_expenses = super_row['Additional Monthly Expenses']

            # Add Super node
            dot.node(superv, f'Super: {superv}\nTotal Sales: ${super_sales:,}\nAvg Salary: ${super_salary:,}\nTotal Expenses: ${super_expenses:,}', shape='box')
            dot.edge(cnf, superv)

            # Get Distributor data for this Super
            distributor_group = data[data['Super'] == superv].groupby('Distributor').agg({
                'Sales - After Closing': 'sum',
                'Salary': 'mean',  # Average salary for Distributor
                'Additional Monthly Expenses': 'sum'  # Total expenses for Distributor
            }).reset_index()

            for _, distributor_row in distributor_group.iterrows():
                distributor = distributor_row['Distributor']
                distributor_sales = distributor_row['Sales - After Closing']
                distributor_salary = distributor_row['Salary']
                distributor_expenses = distributor_row['Additional Monthly Expenses']

                # Add Distributor node
                dot.node(distributor, f'Distributor: {distributor}\nTotal Sales: ${distributor_sales:,}\nAvg Salary: ${distributor_salary:,}\nTotal Expenses: ${distributor_expenses:,}', shape='box')
                dot.edge(superv, distributor)

                # Get RSM data for this Distributor
                rsm_group = data[data['Distributor'] == distributor].groupby('RSM').agg({
                    'Sales - After Closing': 'sum',
                    'Salary': 'mean',  # Average salary for RSM
                    'Additional Monthly Expenses': 'sum'  # Total expenses for RSM
                }).reset_index()

                for _, rsm_row in rsm_group.iterrows():
                    rsm = rsm_row['RSM']
                    rsm_sales = rsm_row['Sales - After Closing']
                    rsm_salary = rsm_row['Salary']
                    rsm_expenses = rsm_row['Additional Monthly Expenses']

                    # Add RSM node
                    dot.node(rsm, f'RSM: {rsm}\nTotal Sales: ${rsm_sales:,}\nAvg Salary: ${rsm_salary:,}\nTotal Expenses: ${rsm_expenses:,}', shape='box')
                    dot.edge(distributor, rsm)

                    # Get ASM data for this RSM
                    asm_group = data[data['RSM'] == rsm].groupby('ASM').agg({
                        'Sales - After Closing': 'sum',
                        'Salary': 'mean',  # Average salary for ASM
                        'Additional Monthly Expenses': 'sum'  # Total expenses for ASM
                    }).reset_index()

                    for _, asm_row in asm_group.iterrows():
                        asm = asm_row['ASM']
                        asm_sales = asm_row['Sales - After Closing']
                        asm_salary = asm_row['Salary']
                        asm_expenses = asm_row['Additional Monthly Expenses']

                        # Add ASM node
                        dot.node(asm, f'ASM: {asm}\nTotal Sales: ${asm_sales:,}\nAvg Salary: ${asm_salary:,}\nTotal Expenses: ${asm_expenses:,}', shape='box')
                        dot.edge(rsm, asm)

                        # Get Employee data for this ASM
                        employee_group = data[data['ASM'] == asm]

                        for _, employee_row in employee_group.iterrows():
                            emp_name = employee_row['Employee Name']
                            emp_sales = employee_row['Sales - After Closing']
                            emp_salary = employee_row['Salary']
                            emp_expenses = employee_row['Additional Monthly Expenses']
                            emp_profit = employee_row['Profit']

                            # Add Employee node
                            dot.node(emp_name, f'Employee: {emp_name}\nSales: ${emp_sales:,}\nSalary: ${emp_salary:,}\nExpenses: ${emp_expenses:,}\nProfit: ${emp_profit:,}', shape='box', color='lightgreen' if emp_profit > 0 else 'lightcoral')
                            dot.edge(asm, emp_name)
    
    return dot

# Generate flow chart
flow_chart = create_flow_chart(data)

# Render flow chart in Streamlit
st.graphviz_chart(flow_chart)
