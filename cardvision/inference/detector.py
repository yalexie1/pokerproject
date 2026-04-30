"""
CardDetector: loads a YOLOv8 model and runs inference on images.

Return schema for detect():
  [{"class": "Ah", "confidence": 0.97, "bbox": [x1, y1, x2, y2]}, ...]
  bbox coordinates are in pixels, relative to the original image size.
"""

from pathlib import Path
from ultralytics import YOLO


class CardDetector:
    def __init__(self, model_path: str, conf_threshold: float = 0.4):
        self._model = YOLO(model_path)
        self._conf = conf_threshold

    def detect(self, image_path: str) -> list[dict]:
        results = self._model.predict(
            source=image_path,
            conf=self._conf,
            verbose=False,
        )
        detections = []
        for result in results:
            names = result.names
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append({
                    "class": names[int(box.cls)],
                    "confidence": round(float(box.conf), 4),
                    "bbox": [round(x1), round(y1), round(x2), round(y2)],
                })
        return detections
