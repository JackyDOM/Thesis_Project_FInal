import easyocr
import cv2
import torch
import random
import numpy as np
from collections import defaultdict

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Initialize YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
model.conf = 0.3
model.iou = 0.4

# Read and resize image
img = cv2.imread('image_test_case.png')
scale_percent = 70
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
img_resized = cv2.resize(img, (width, height))

# YOLO Detection
results = model(img_resized)
detections = results.pandas().xyxy[0]

for _, det in detections.iterrows():
    if det['confidence'] > 0.25:
        x1, y1, x2, y2 = int(det['xmin']), int(det['ymin']), int(det['xmax']), int(det['ymax'])
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        cv2.rectangle(img_resized, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img_resized, f"{det['name']} {det['confidence']:.2f}",
                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

# EasyOCR Processing
ocr_results = reader.readtext(img_resized, paragraph=False, detail=1, batch_size=10, width_ths=0.4)
custom_labels = ['First Name', 'Second Name', 'Age', 'Gender', 'Email',
                 'School Name', 'Address', 'City', 'Result']

def get_y_center(bbox):
    return (bbox[0][1] + bbox[2][1]) / 2

def get_x_center(bbox):
    return (bbox[0][0] + bbox[2][0]) / 2

rows = defaultdict(list)
for bbox, text, prob in ocr_results:
    y_center = get_y_center(bbox)
    rows[round(y_center / 10) * 10].append((bbox, text.strip(), prob))

sorted_rows = sorted(rows.items(), key=lambda x: x[0])

for row_idx, (y_pos, row_items) in enumerate(sorted_rows):
    row_items.sort(key=lambda x: get_x_center(x[0]))
    print(f"\nRow {row_idx + 1}:")
    
    row_texts = [text for _, text, _ in row_items]
    
    if row_idx == 0:  # Ensure proper header alignment
        row_texts = custom_labels[:len(row_texts)]
    
    if len(row_texts) == len(custom_labels):
        for col_idx, text in enumerate(row_texts):
            print(f"  {custom_labels[col_idx]}: {text}")
    elif len(row_texts) >= 2:  # Avoid rows with too little data
        for col_idx, text in enumerate(row_texts):
            label = custom_labels[min(col_idx, len(custom_labels)-1)]
            print(f"  {label}: {text}")
            
    # Draw bounding boxes for OCR detected text
    for bbox, text, _ in row_items:
        color = (0, 255, 0)  # Green for all detected text
        cv2.rectangle(img_resized, tuple(map(int, bbox[0])), tuple(map(int, bbox[2])), color, 2)
        cv2.putText(img_resized, text,
                    (int(bbox[0][0]), int(bbox[0][1]-5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
cv2.imshow('Combined Detection', img_resized)
cv2.waitKey(0)
cv2.destroyAllWindows()
