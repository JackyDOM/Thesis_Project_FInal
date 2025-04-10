from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import numpy as np
import random
import os

# Create the folder structure if it doesn't exist
output_dir = os.path.join("static", "dataset")
os.makedirs(output_dir, exist_ok=True)

# Create a sample dataset with random data for each image
def generate_random_data(num_rows=5):
    data = {
        "First Name": [f"Name{i}" for i in range(num_rows)],
        "Second Name": [f"Surname{i}" for i in range(num_rows)],
        "Age": [random.randint(18, 25) for _ in range(num_rows)],
        "Gender": [random.choice(["Male", "Female"]) for _ in range(num_rows)],
        "Email": [f"email{i}@gmail.com" for i in range(num_rows)],
        "School Name": [f"School{random.randint(1, 10)}" for i in range(num_rows)],
        "Address": [f"St {random.randint(50, 99)} Hm{random.randint(10, 99)}" for i in range(num_rows)],
        "City": [random.choice(["P.Penh", "Siem Reap", "Battambang"]) for i in range(num_rows)],
        "Result": [random.choice(["Pass", "Fail"]) for i in range(num_rows)]
    }
    df = pd.DataFrame(data)
    # Randomize the column order
    columns = list(df.columns)
    random.shuffle(columns)
    df = df[columns]
    return df

# Convert the table to an image with more spacing at the top
def create_table_image(df, output_path):
    # Create a blank image with a wider width to accommodate all columns
    img = Image.new("RGB", (1200, 400), color=(255, 255, 255))  # Pure white background
    draw = ImageDraw.Draw(img)

    # Try to use a more readable font with a smaller size
    try:
        font = ImageFont.truetype("arial.ttf", 12)  # Smaller font size to match the example
    except:
        font = ImageFont.load_default()

    # Calculate column widths based on the actual text width in pixels
    col_widths = []
    for col in df.columns:
        # Get the maximum length of the column name and its values
        max_len = max(df[col].astype(str).map(len).max(), len(col))
        # Estimate the width using the font's bounding box for more accuracy
        text_width = 0
        for _, row in df.iterrows():
            text = str(row[col])
            bbox = draw.textbbox((0, 0), text, font=font)
            width = bbox[2] - bbox[0]  # Right - Left
            text_width = max(text_width, width)
        # Also calculate the width of the column header
        header_bbox = draw.textbbox((0, 0), col, font=font)
        header_width = header_bbox[2] - header_bbox[0]
        # Use the maximum of the header width and the column data width
        col_widths.append(max(text_width, header_width) + 20)  # Add extra padding

    # Draw the table headers (without borders, with more space at the top)
    x_offset = 10
    y_offset = 30  # Increased from 10 to 30 for more space at the top
    for i, col in enumerate(df.columns):
        draw.text((x_offset, y_offset), col, fill="black", font=font)
        x_offset += col_widths[i] + 30  # Spacing between columns

    # Draw the table rows (without borders, with more vertical spacing)
    y_offset += 30  # Space between header and first row
    for _, row in df.iterrows():
        x_offset = 10
        for i, value in enumerate(row):
            draw.text((x_offset, y_offset), str(value), fill="black", font=font)
            x_offset += col_widths[i] + 30  # Spacing between columns
        y_offset += 40  # Row height for more vertical spacing

    # Save the image
    img.save(output_path)

# Generate 40 synthetic images with random data and randomized column order
for i in range(50):
    # Generate new random data for each image with randomized column order
    df = generate_random_data(num_rows=random.randint(2, 5))  # Random number of rows between 2 and 5
    output_path = os.path.join(output_dir, f"table_image_{i}.png")
    create_table_image(df, output_path)
    print(f"Generated image: {output_path}")

    