import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import base64
from PIL import Image

# Function to create a report as an image
def create_employee_report(employee_data, total_sales, total_expenses, average_salary, target, profit, target_percentage, color):
    # Prepare data for report
    emp_name = employee_data['Employee Name'].iloc[0]
    report_text = f"""
    Employee Name: {emp_name}
    Total Sales: ₹{total_sales:,.2f}
    Target Sales: ₹{target:,.2f}
    Salary: ₹{average_salary:,.2f}
    Total Expenses: ₹{total_expenses:,.2f}
    Profit: ₹{profit:,.2f} ({'Profit' if profit > 0 else 'Loss'})
    Target Achievement: {target_percentage:.2f}%
    """

    # Create a figure for the report
    fig, ax = plt.subplots(figsize=(6, 8))

    # Remove axis
    ax.axis('off')

    # Add title
    ax.text(0.5, 1.05, f"Employee Final Report: {emp_name}", fontsize=18, ha='center', va='center', fontweight='bold')

    # Add report text
    ax.text(0.5, 0.85, report_text, fontsize=12, ha='center', va='top', wrap=True, bbox=dict(facecolor='lightgray', edgecolor='black', boxstyle='round,pad=0.3'))

    # Add target achievement bar (color-coded)
    ax.barh([0], [target_percentage], color=color, edgecolor='black', height=0.3, alpha=0.8)
    ax.text(0.5, 0.6, f"Target Achievement: {target_percentage:.2f}%", fontsize=14, ha='center', va='center', color='white')

    # Save image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img = Image.open(buffer)
    return img

# Example: Assume the filtered_data is passed from earlier steps in your code
# For the sake of this example, using mock data
# Replace this with actual filtered data from earlier steps
employee_data = data[data['Employee Name'] == selected_employee]  # Assuming selected_employee is defined earlier
total_sales = employee_data['Sales - After Closing'].sum()
total_expenses = employee_data['Additional Monthly Expenses'].sum()
average_salary = employee_data['Salary'].mean()
employee_target = employee_data['Target'].mean()
profit = total_sales - total_expenses
target_percentage = (total_sales / employee_target) * 100 if employee_target > 0 else 0

# Set color based on target achievement
if target_percentage >= 90:
    color = 'green'
elif target_percentage >= 50:
    color = 'yellow'
elif target_percentage >= 30:
    color = 'orange'
else:
    color = 'red'

# Generate the report image
employee_report_image = create_employee_report(employee_data, total_sales, total_expenses, average_salary, employee_target, profit, target_percentage, color)

# Display the report image
st.image(employee_report_image, caption=f"Final Report for {employee_data['Employee Name'].iloc[0]}", use_column_width=True)
