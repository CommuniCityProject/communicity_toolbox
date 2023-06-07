# RetinaFace

RetinaFace is a single-stage face detector implemented in [PyTorch](https://pytorch.org/) based on the original paper ["RetinaFace: Single-stage Dense Face Localisation in the Wild"](https://arxiv.org/abs/1905.00641).

The official code can be found [here](https://github.com/biubug6/Pytorch_Retinaface).

Weights are available in the [releases](https://github.com/CommuniCityProject/communicity_toolbox/releases) section of the repository:
- Resnet50: ``data/models/face_detector_retinaface/mobilenet0.25_Final.pth``
- Mobilenet0.25: ``data/models/face_detector_retinaface/Resnet50_Final.pth``

### Performance on [WIDER](http://shuoyang1213.me/WIDERFACE/) Face Val dataset

| Backbone | AP - easy | AP - medium | AP - hard | Inference time (s/img) - CPU | Inference time (s/img) - GPU|
|-|-|-|-|-|-|
| Resnet50 | 95.48% |94.04% | 84.43% | 3.617 | 0.136 |
| Mobilenet0.25 | 90.70% | 88.16% | 73.82% | 0.253 | 0.120 |

<sup>**CPU:** Intel(R) Xeon(R) Silver 4116 || **GPU:** Quadro RTX 8000</sup>

### Usage example

```python
import cv2
from toolbox.Models.face_detector_retinaface import FaceDetector

img = cv2.imread("data/samples/images/faces/celeb/ben_mad_min_jer.png")

detector = FaceDetector(
    weights_path="data/models/face_detector_retinaface/mobilenet0.25_Final.pth", 
    model_name="mobile0.25",
    use_cuda=False
)
instances = detector.predict(img)

print(instances[0].fields)
# > ['bounding_box', 'confidence']

for instance in instances:
    print(instance.bounding_box, instance.confidence)
# > BoundingBox(0.130,0.565,0.360,0.800) 0.9999852
# > BoundingBox(0.604,0.077,0.838,0.350) 0.9998944
# > BoundingBox(0.580,0.565,0.800,0.853) 0.9998043
# > BoundingBox(0.104,0.073,0.300,0.313) 0.99966705
```

### Project configuration YAML example:

```yaml
face_detector:
    model_name: face_detector_retinaface
    params:
      weights_path: ../../../data/models/face_detector_retinaface/Resnet50_Final.pth
      model_name: resnet50
      confidence_threshold: 0.7
      landmarks: False
      nms_threshold: 0.4
      max_input_size: 512
      use_cuda: True
```

<details>
<summary>Note:</summary>

The model may struggle to detect large faces since it was trained with anchors ranging from 16 to 512 pixels. To address this issue, use the parameter ``max_input_size`` to scale down larger images (e.g. ``512``). It can also be used to speed up inference.
    
</details>