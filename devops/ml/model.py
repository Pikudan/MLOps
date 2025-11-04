#  <#Title#>
import ultralytics
from ultralytics import YOLO
import numpy as np
import cv2
import albumentations as A
import json
from pathlib import Path
import yaml

def bgr2rgb(image, **params):
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)



def detect(image, plant) -> json.JSONEncoder:
    # load config file
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    file.close()
    imgsz = config["models"]["detect"][plant]["image_size"]
    ratio = max(image.shape[0:2]) / imgsz
    # resize to imgsz * imgsz and convert bgr to rgb
    inference_aug = A.Compose(
        [
            A.LongestMaxSize(max_size=imgsz, interpolation=1),
            A.PadIfNeeded(min_height=imgsz, min_width=imgsz, border_mode=0, value=(0,0,0), position=A.PadIfNeeded.PositionType.TOP_LEFT),
            A.Lambda(image=bgr2rgb),
        ],
        p=1,
    )
    transform_image = inference_aug(image=image)["image"]
    weights=config["models"]["detect"][plant]["weights"]
    model = YOLO(weights)
    results = model.predict(transform_image, show=True, save=False, imgsz=imgsz)
    boxes = results[0].boxes.xyxy.tolist()
    clss = results[0].boxes.cls.tolist()
    names = results[0].names
    confs = results[0].boxes.conf.tolist()

    ultralytics_json = []
    for box, cls, conf in zip(boxes, clss, confs):
        x1, x2, y1, y2 = box
        conf = str(int(conf * 100))+"%"
        name = names[int(cls)]

        box_data = {
            "name": name,
            "class": int(cls),
            "confidence": conf,
            "box": {
                "x1": x1 * ratio,
                "x2": x2 * ratio,
                "y1": y1 * ratio,
                "y2": y2 * ratio,
            }
        }

        ultralytics_json.append(box_data)
    result = json.dumps(ultralytics_json, indent=4)
    return json.loads(result)
    
def model(image, task, plant) -> json.JSONEncoder:
    if task == "detect":
        return detect(image, plant)
    if task == "disease":
        return disease(image, plant)

