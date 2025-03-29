# import cv2
# import torch

# # Load YOLOv5 model (pre-trained on COCO dataset)
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# # Set up webcam
# cap = cv2.VideoCapture(0)  # Use 0 for the default webcam
# if not cap.isOpened():
#     print("Error: Could not open webcam.")
#     exit()

# while True:
#     # Capture frame from webcam
#     ret, frame = cap.read()
#     if not ret:
#         print("Error: Could not read frame.")
#         break

#     # Convert frame from BGR to RGB (YOLO expects RGB)
#     img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#     # Run YOLOv5 inference
#     results = model(img_rgb)

#     # Extract bounding boxes, confidence scores, and class labels
#     detections = results.xyxy[0]  # Get detections

#     for detection in detections:
#         x1, y1, x2, y2, conf, cls = detection  # YOLOv5 output: [x1, y1, x2, y2, confidence, class]
#         x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])  # Convert to integers
#         conf = conf.item()  # Confidence score
#         cls = int(cls.item())  # Class index
#         label = f"{model.names[cls]} ({conf:.2f})"  # Get class name and confidence

#         if conf > 0.3:  # Only draw boxes with confidence > 30%
#             # Draw bounding box
#             cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#             # Draw label
#             cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#     # Display the frame with detections
#     cv2.imshow("YOLOv5 Live Object Detection", frame)

#     # Exit on 'q' key press
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release resources
# cap.release()
# cv2.destroyAllWindows()


# Import PyTorch module
# import torch
# import cv2

# # Download model from github
# model = torch.hub.load('ultralytics/yolov5', 'yolov5n')
    
# img = cv2.imread('test.png')
# img = cv2.resize(img,(1000, 650))

# # Perform detection on image
# result = model(img)
# print('result: ', result)

# # Convert detected result to pandas data frame
# data_frame = result.pandas().xyxy[0]
# print('data_frame:')
# print(data_frame)

# # Get indexes of all of the rows
# indexes = data_frame.index
# for index in indexes:
#     # Find the coordinate of top left corner of bounding box
#     x1 = int(data_frame['xmin'][index])
#     y1 = int(data_frame['ymin'][index])
#     # Find the coordinate of right bottom corner of bounding box
#     x2 = int(data_frame['xmax'][index])
#     y2 = int(data_frame['ymax'][index ])

#     # Find label name
#     label = data_frame['name'][index ]
#     # Find confidance score of the model
#     conf = data_frame['confidence'][index]
#     text = label + ' ' + str(conf.round(decimals= 2))

#     cv2.rectangle(img, (x1,y1), (x2,y2), (255,255,0), 2)
#     cv2.putText(img, text, (x1,y1-5), cv2.FONT_HERSHEY_PLAIN, 2,
#                 (255,255,0), 2)

# cv2.imshow('IMAGE', img)
# cv2.waitKey(0)

# import easyocr
# import cv2

# # Initialize EasyOCR reader
# reader = easyocr.Reader(['en'])

# # Read image
# img = cv2.imread('test.png')

# # Resize the image if it's too large
# scale_percent = 70  # Adjust this scale as needed
# width = int(img.shape[1] * scale_percent / 100)
# height = int(img.shape[0] * scale_percent / 100)
# img = cv2.resize(img, (width, height))

# # Perform text detection
# results = reader.readtext(img)

# # Draw bounding boxes around detected text with proper spacing
# for (bbox, text, prob) in results:
#     (x1, y1), (x2, y2), (x3, y3), (x4, y4) = bbox

#     # Convert coordinates to integers
#     x1, y1, x3, y3 = int(x1), int(y1), int(x3), int(y3)

#     # Draw rectangle with padding
#     cv2.rectangle(img, (x1 - 10, y1 - 10), (x3 + 10, y3 + 10), (255, 255, 0), 2)

#     # Calculate text size for spacing
#     text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
#     text_height = text_size[1] + 10  # Extra spacing

#     # Adjust text position with spacing
#     text_y = max(y1 - 15, 20)  # Prevent text from going off-screen
#     for i, line in enumerate(text.split()):  # If multiple words, display them separately
#         line_y = text_y + (i * text_height)  # Space out each line
#         cv2.putText(img, line, (x1, line_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

# # Resize window to fit screen
# cv2.namedWindow('Image', cv2.WINDOW_NORMAL)  
# cv2.imshow('Image', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


import easyocr
import cv2
import torch
import random

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Initialize YOLOv5 model (Pre-trained)
model = torch.hub.load('ultralytics/yolov5', 'yolov5n')  # Use 'yolov5s' for small model or 'yolov5m'/'yolov5l' for larger models

# Read image
img = cv2.imread('test.png')

# Resize the image if it's too large
scale_percent = 70  # Adjust this scale as needed
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
img_resized = cv2.resize(img, (width, height))

# Perform YOLOv5 object detection
results = model(img_resized)

# Get the detected bounding boxes for text-related objects
text_bboxes = results.xywh[0]  # Bounding boxes, classes, and confidence scores

# Check if YOLO detected anything
print(f"Number of detections: {len(text_bboxes)}")

# Draw YOLO detections (Object detection boxes)
for bbox in text_bboxes:
    x_center, y_center, w, h, conf, cls = bbox

    if conf > 0.5:  # Threshold for confidence; adjust as needed
        # Convert YOLO bounding box from center format to corner format
        x1 = int((x_center - w / 2))
        y1 = int((y_center - h / 2))
        x2 = int((x_center + w / 2))
        y2 = int((y_center + h / 2))
        
        # Generate a random color for the bounding box (RGB format)
        color = [random.randint(0, 255) for _ in range(3)]  # Random color for each object
        
        # Draw bounding box for detected object (YOLO)
        cv2.rectangle(img_resized, (x1, y1), (x2, y2), color, 2)  # Bounding box with random color
        label = f"Object {int(cls)}"  # Label as object
        cv2.putText(img_resized, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

# Perform text detection using EasyOCR
ocr_results = reader.readtext(img_resized)

# List of custom labels for each column
custom_labels = ['First Name', 'Second Name', 'Age', 'Gender', 'Email', 'School Name', 'Address', 'City', 'Result']

# Helper functions to get y-center, x-start, and x-end of a bounding box
def get_y_center(bbox):
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = bbox
    return (y1 + y3) / 2

def get_x_start(bbox):
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = bbox
    return x1

def get_x_end(bbox):
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = bbox
    return x3

# Step 1: Sort OCR results by y-coordinate (to group by rows) and then by x-coordinate (to order within rows)
ocr_results_sorted = sorted(ocr_results, key=lambda x: (get_y_center(x[0]), get_x_start(x[0])))

# Step 2: Group OCR results into rows based on y-coordinates
rows = []
current_row = []
last_y = None
y_threshold = 50  # Increased to better group text within the same row

for result in ocr_results_sorted:
    bbox, text, prob = result
    y_center = get_y_center(bbox)
    
    if last_y is None or abs(y_center - last_y) < y_threshold:
        current_row.append(result)
    else:
        rows.append(current_row)
        current_row = [result]
    last_y = y_center

# Add the last row
if current_row:
    rows.append(current_row)

# Debug: Print the number of rows
print(f"Total rows detected: {len(rows)}")

# Step 3: Skip the header row (first row) and process data rows
data_rows = rows[1:]  # Skip the first row (header)

# Step 4: Estimate column boundaries from the header row
header_row = rows[0]  # First row is the header
header_items = sorted(header_row, key=lambda x: get_x_start(x[0]))
column_boundaries = []
for idx, (bbox, text, prob) in enumerate(header_items):
    x_start = get_x_start(bbox)
    x_end = get_x_end(bbox)
    if idx == 0:
        column_boundaries.append(x_start)
    if idx == len(header_items) - 1:
        column_boundaries.append(x_end)
    else:
        next_x_start = get_x_start(header_items[idx + 1][0])
        boundary = (x_end + next_x_start) / 2
        column_boundaries.append(boundary)

# Debug: Print column boundaries
print("Column boundaries:", column_boundaries)

# Step 5: Merge split text detections within each row using column boundaries
def merge_split_text(row, column_boundaries):
    # Sort the row by x-coordinate
    row_sorted = sorted(row, key=lambda x: get_x_start(x[0]))

    # Assign each text item to a column based on its x-coordinate
    column_items = [[] for _ in range(len(custom_labels))]
    for bbox, text, prob in row_sorted:
        x_center = (get_x_start(bbox) + get_x_end(bbox)) / 2
        # Find the column this text belongs to
        for col_idx in range(len(column_boundaries) - 1):
            if column_boundaries[col_idx] <= x_center < column_boundaries[col_idx + 1]:
                column_items[col_idx].append((bbox, text, prob))
                break

    # Merge text within each column
    merged_row = []
    for col_idx, items in enumerate(column_items):
        if not items:
            # If the column is empty, add a placeholder
            merged_row.append(([(0, 0), (0, 0), (0, 0), (0, 0)], "", 0.0))
        else:
            # Merge all items in this column
            combined_text = " ".join(item[1] for item in items)
            # Use the bounding box of the first item (or combine them)
            bbox = items[0][0]
            prob = max(item[2] for item in items)
            if len(items) > 1:
                # Combine bounding boxes
                (x1, y1), (x2, y2), (x3, y3), (x4, y4) = bbox
                for other_bbox, _, _ in items[1:]:
                    (nx1, ny1), (nx2, ny2), (nx3, ny3), (nx4, ny4) = other_bbox
                    x1 = min(x1, nx1)
                    y1 = min(y1, ny1)
                    x2 = max(x2, nx2)
                    y2 = max(y2, ny2)
                    x3 = max(x3, nx3)
                    y3 = max(y3, ny3)
                    x4 = min(x4, nx4)
                    y4 = min(y4, ny4)
                bbox = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
            merged_row.append((bbox, combined_text, prob))

    return merged_row

# Step 6: Process each row, merge split text, and assign labels
for row_idx, row in enumerate(data_rows):
    # Merge split text within the row using column boundaries
    merged_row = merge_split_text(row, column_boundaries)
    
    # Debug: Print the merged row to verify the text
    print(f"Row {row_idx + 1}:")
    for idx, (bbox, text, prob) in enumerate(merged_row):
        print(f"  Column {idx + 1} ({custom_labels[idx]}): {text}")

    # Assign labels to each column in the row
    for idx, (bbox, text, prob) in enumerate(merged_row):
        if text == "":
            continue  # Skip empty items (from padding)

        (x1_text, y1_text), (x2_text, y2_text), (x3_text, y3_text), (x4_text, y4_text) = bbox
        x1_text, y1_text, x3_text, y3_text = int(x1_text), int(y1_text), int(x3_text), int(y3_text)

        # Generate a random color for each OCR text bounding box
        color = [random.randint(0, 255) for _ in range(3)]  # Random color for each bounding box

        # Assign the custom label based on the column index
        label = custom_labels[idx] if idx < len(custom_labels) else "Text"
        cv2.rectangle(img_resized, (x1_text - 10, y1_text - 10), (x3_text + 10, y3_text + 10), color, 2)
        cv2.putText(img_resized, label, (x1_text, y1_text - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

# Resize window to fit screen
cv2.namedWindow('Image', cv2.WINDOW_NORMAL)  
cv2.imshow('Image', img_resized)
cv2.waitKey(0)
cv2.destroyAllWindows()