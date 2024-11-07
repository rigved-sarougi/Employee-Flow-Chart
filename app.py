import streamlit as st
import pandas as pd
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

# Format currency with the Rs symbol and commas for thousands
def format_currency(value):
    return f"Rs {value:,.2f}"

# Calculate target achievement percentage and color code
target_percentage = (total_sales / employee_target) * 100 if employee_target > 0 else 0
if target_percentage >= 90:
    color = '#28a745'  # Green for above 90%
elif target_percentage >= 50:
    color = '#ffc107'  # Yellow for above 50%
elif target_percentage >= 30:
    color = '#fd7e14'  # Orange for above 30%
else:
    color = '#dc3545'  # Red for below 30%

# Employee Performance Summary
performance_summary = f"""
Employee Performance Summary:
---------------------------
Employee Name: {filtered_data['Employee Name'].iloc[0]}
Total Sales: {format_currency(total_sales)}

Target: {format_currency(employee_target)}

Total Expenses: {format_currency(total_expenses)}

Salary: {format_currency(average_salary)}

Profit: {('+' if profit > 0 else '')}{format_currency(profit)} ({'Profit' if profit > 0 else 'Loss'})

Target Achievement: {target_percentage:.2f}%
"""

# Create a more professional and styled image of the performance summary
def generate_professional_performance_summary_image(summary_text, target_percentage):
    # Create a blank image with white background
    img_width, img_height = 700, 400
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)

    # Define the font and size (you can change the font as needed)
    try:
        font_header = ImageFont.truetype("arialbd.ttf", 18)  # Bold font for header
        font_body = ImageFont.truetype("arial.ttf", 16)  # Regular font for body
    except IOError:
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()

    # Draw a border around the image
    border_color = "#007bff"  # Blue border color
    draw.rectangle([5, 5, img_width-5, img_height-5], outline=border_color, width=3)

    # Add a title header with a different color
    title_color = "#007bff"  # Blue color for the title
    draw.text((20, 20), "Employee Performance Summary", font=font_header, fill=title_color)

    # Add the summary content with proper spacing
    margin_top = 50
    draw.text((20, margin_top), summary_text, font=font_body, fill="black")

    # Add a colored background for target achievement status
    achievement_color = color
    achievement_box_height = 30
    draw.rectangle([20, img_height - 70, img_width - 20, img_height - 20], fill=achievement_color)

    # Add the target achievement text at the bottom
    target_text = f"Target Achievement: {target_percentage:.2f}%"
    draw.text((20, img_height - 60), target_text, font=font_body, fill="white")

    # Save the image in a BytesIO object
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    return img_io

# Generate the professional performance summary image
img_io = generate_professional_performance_summary_image(performance_summary, target_percentage)

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
