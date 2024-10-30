
from ultralytics import YOLO

model = YOLO('best.pt')

result = model.predict('test3_img.jpg', imgsz=640, conf=0.1)

for res in result:
    res.show()