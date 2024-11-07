import streamlit as st
import pandas as pd
from graphviz import Digraph
from PIL import Image, ImageDraw, ImageFont
import io

# Load data from CSV
data = pd.read_csv('data.csv')

# Calculate expenses, profit, and profit status
data['Total Expenses'] = data['Salary'] + data['Additional Monthly Expenses']
data['Profit'] = data['Sales - After Closing'] - data['Total Expenses']
data['Profit Status'] = data['Profit'].apply(lambda x: 'Profit' if x > 0 else 'Loss')

# Streamlit app setup
st.title("🌟Biolume - Employee Sales Flow Chart with Performance Matrix")
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

# Employee Performance Summary
performance_summary = f"""
Employee Performance Summary:
---------------------------
Employee Name: {filtered_data['Employee Name'].iloc[0]}
Total Sales: ₹{total_sales:,.2f}
Target: ₹{employee_target:,.2f}
Total Expenses: ₹{total_expenses:,.2f}
Salary: ₹{average_salary:,.2f}
Profit: ₹{'+' if profit > 0 else ''}₹{profit:,.2f} ({'Profit' if profit > 0 else 'Loss'})
Target Achievement: {target_percentage:.2f}%
"""

# Create image of performance summary
def generate_performance_summary_image(summary_text):
    # Create a blank image with white background
    img = Image.new('RGB', (600, 300), color='white')
    draw = ImageDraw.Draw(img)

    # Define the font and size (you can change the font as needed)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()

    # Add the performance summary text
    draw.text((10, 10), summary_text, font=font, fill="black")

    # Save the image in a BytesIO object
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    return img_io

# Generate the performance summary image
img_io = generate_performance_summary_image(performance_summary)

# Display the image in Streamlit
st.subheader("📊 Employee Performance Summary with Target Achievement")
st.image(img_io, caption='Employee Performance Summary', use_column_width=True)

# Provide a download link for the image
st.download_button(
    label="Download Employee Performance Summary",
    data=img_io,
    file_name="employee_performance_summary.png",
    mime="image/png"
)
