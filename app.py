# Function to create the flow chart
def create_flow_chart(employee_data):
    dot = Digraph()
    
    # Calculate total sales per CNF, Super, Distributor, and RSM
    total_sales = employee_data.groupby(['CNF', 'Super']).agg({
        'Sales - After Closing': 'sum'
    }).reset_index()
    
    for index, row in employee_data.iterrows():
        cnf = row['CNF']
        superv = row['Super']
        distributor = row['Distributor']
        rsm = row['RSM']
        asm = row['ASM']
        emp_name = row['Employee Name']
        sales = row['Sales - After Closing']
        salary = employee_data['Salary'].mean()  # Average salary for employees in this group
        expenses = employee_data['Additional Monthly Expenses'].sum()  # Total monthly expenses for this group
        profit = sales - (salary + expenses)

        # Calculate cumulative sales for CNF and Super
        cnf_sales = total_sales[total_sales['CNF'] == cnf]['Sales - After Closing'].sum()
        super_sales = employee_data[employee_data['Super'] == superv]['Sales - After Closing'].sum()
        
        # Add nodes for CNF, Super, Distributor, RSM, ASM, Employee
        dot.node(cnf, f'CNF: {cnf}\nSales: ${cnf_sales:,}', shape='box')
        dot.node(superv, f'Super: {superv}\nSales: ${super_sales:,}', shape='box')
        dot.node(distributor, f'Distributor: {distributor}\nSales: ${sales:,}', shape='box')
        dot.node(rsm, f'RSM: {rsm}\nSales: ${sales:,}', shape='box')
        dot.node(asm, f'ASM: {asm}\nSales: ${sales:,}', shape='box')
        dot.node(emp_name, f'Employee: {emp_name}\nSales: ${sales:,}\nSalary: ${salary:,.2f}\nExpenses: ${expenses:,.2f}\nProfit: ${profit:,.2f}', 
                 shape='box', color='lightgreen' if profit > 0 else 'lightcoral')
        
        # Create edges
        dot.edge(cnf, superv)
        dot.edge(superv, distributor)
        dot.edge(distributor, rsm)
        dot.edge(rsm, asm)
        dot.edge(asm, emp_name)
    
    return dot
