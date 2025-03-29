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

import easyocr
import cv2

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Read image
img = cv2.imread('test.png')

# Resize the image if it's too large
scale_percent = 70  # Adjust this scale as needed
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
img = cv2.resize(img, (width, height))

# Perform text detection
results = reader.readtext(img)

# Draw bounding boxes around detected text with proper spacing
for (bbox, text, prob) in results:
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = bbox

    # Convert coordinates to integers
    x1, y1, x3, y3 = int(x1), int(y1), int(x3), int(y3)

    # Draw rectangle with padding
    cv2.rectangle(img, (x1 - 10, y1 - 10), (x3 + 10, y3 + 10), (255, 255, 0), 2)

    # Calculate text size for spacing
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
    text_height = text_size[1] + 10  # Extra spacing

    # Adjust text position with spacing
    text_y = max(y1 - 15, 20)  # Prevent text from going off-screen
    for i, line in enumerate(text.split()):  # If multiple words, display them separately
        line_y = text_y + (i * text_height)  # Space out each line
        cv2.putText(img, line, (x1, line_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

# Resize window to fit screen
cv2.namedWindow('Image', cv2.WINDOW_NORMAL)  
cv2.imshow('Image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()


