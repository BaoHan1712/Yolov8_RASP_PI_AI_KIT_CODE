from ultralytics import YOLO

# Load a pretrained YOLO11n model
model = YOLO("model\2clss_yolov8_ver1.pt")

model.export(format="onnx",half = True, simplify=True, imgsz=640)

# # # # Run inference on 'bus.jpg' with arguments
# model.predict(source=0, imgsz=480,conf = 0.65, show = True)

## Show class name
# print(model.names) 