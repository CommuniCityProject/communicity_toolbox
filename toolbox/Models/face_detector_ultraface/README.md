# UltraFace

UltraFace is a lightweight face detector designed for edge computing devices.

The official code can be found [here](https://github.com/Linzaer/Ultra-Light-Fast-Generic-Face-Detector-1MB).

Weights are available in the [releases](https://github.com/CommuniCityProject/communicity_toolbox/releases) section of the repository:
- version-RFB-640.onnx: ``data/models/face_detector_ultraface/version-RFB-640.onnx``
- version-RFB-320.onnx: ``data/models/face_detector_ultraface/version-RFB-320.onnx``

### Performance on [WIDER](http://shuoyang1213.me/WIDERFACE/) Face Val dataset

| Backbone | Input size (W, H) | AP - easy | AP - medium | AP - hard | Inference time (s/img) - CPU | Inference time (s/img) - GPU|
|-|-|-|-|-|-|-|
| version-RFB-640 | (640, 480) | 85.5% | 82.2% | 57.9% | 0.0675 | 0.0191 |
| version-RFB-320 | (320, 240) | 78.7% | 69.8% | 43.8% | 0.0251 | 0.0085 |

<sup>**CPU:** Intel(R) Xeon(R) Silver 4116 || **GPU:** Quadro RTX 8000</sup>

### Usage example

```python
import cv2
from toolbox.Models.face_detector_ultraface import FaceDetector

img = cv2.imread("data/samples/images/faces/celeb/ben_mad_min_jer.png")

detector = FaceDetector(
    model_path="../../../data/models/face_detector_ultraface/version-RFB-640.onnx",
    input_size=(640, 480),
    use_cuda=False
)

instances = detector.predict(img)

print(instances[0].fields)
# > ['bounding_box', 'confidence']

for instance in instances:
    print(instance.bounding_box, instance.confidence)
# > BoundingBox(0.128,0.552,0.358,0.780) 0.99999964
# > BoundingBox(0.580,0.542,0.806,0.840) 0.99998796
# > BoundingBox(0.600,0.075,0.854,0.343) 0.999987
# > BoundingBox(0.108,0.082,0.290,0.312) 0.99997556
```

### Project configuration YAML example:

```yaml
face_detector:
    model_name: face_detector_ultraface
    params:
      model_path: ../../../data/models/face_detector_ultraface/version-RFB-320.onnx
      input_size: [320, 240]
      use_cuda: True
```
