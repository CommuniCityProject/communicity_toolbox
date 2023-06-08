# Detectron2

Detectron2 is a library that provides state-of-the-art detection and segmentation algorithms implemented in [PyTorch](https://pytorch.org/).

The official code can be found [here](https://github.com/facebookresearch/detectron2).

Weights are available in the [releases](https://github.com/CommuniCityProject/communicity_toolbox/releases) section of the repository and online:


## Instance Segmentation

Models:

- mask_rcnn_R_50_FPN_3x:
  - ``data/models/detectron2/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/model_final_f10217.pkl``
  - [https://dl.fbaipublicfiles.com/detectron2/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl](https://dl.fbaipublicfiles.com/detectron2/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl)
- mask_rcnn_X_101_32x8d_FPN_3x:
  - ``data/models/detectron2/COCO-InstanceSegmentation/mask_rcnn_X_101_32x8d_FPN_3x/model_final_2d9806.pkl``
  - [https://dl.fbaipublicfiles.com/detectron2/COCO-InstanceSegmentation/mask_rcnn_X_101_32x8d_FPN_3x/139653917/model_final_2d9806.pkl](https://dl.fbaipublicfiles.com/detectron2/COCO-InstanceSegmentation/mask_rcnn_X_101_32x8d_FPN_3x/139653917/model_final_2d9806.pkl)

### Performance on [COCO](https://cocodataset.org) dataset
| Backbone | box AP| mask AP | Inference time (s/img) - CPU | Inference time (s/img) - GPU|
|-|-|-|-|-|
| mask_rcnn_R_50_FPN_3x | 41.0% | 37.2% | 6.4292 | 0.0690 |
| mask_rcnn_X_101_32x8d_FPN_3x | 44.3% | 39.5% | 21.2994 | 0.1598 |

<sup>**CPU:** Intel(R) Xeon(R) Silver 4116 || **GPU:** Quadro RTX 8000</sup>

### Usage example

```python
import cv2
from toolbox.Models.detectron2 import Detectron2

img = cv2.imread("data/samples/images/general/house_00.jpg")

detectron = Detectron2(
    model_config="data/models/detectron2/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/mask_rcnn_R_50_FPN_3x.yaml",
    model_weights="data/models/detectron2/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/model_final_f10217.pkl",
    use_cuda=False
)

instances = detectron.predict(img)

print(len(instances))
# > 8

print(instances[0].fields)
# > ['confidence', 'label_id', 'label', 'bounding_box', 'mask']

for instance in instances:
    print(f"{instance.label} ({instance.label_id}): {instance.confidence} \t {instance.bounding_box} \t {instance.mask}")
# > dog (16): 0.9980881810188293     BoundingBox(0.403,0.806,0.723,0.992)    SegmentationMask (4032 X 3024)
# > chair (56): 0.9835169911384583   BoundingBox(0.206,0.726,0.393,0.998)    SegmentationMask (4032 X 3024)
# > couch (57): 0.964159369468689    BoundingBox(0.106,0.494,0.438,0.750)    SegmentationMask (4032 X 3024)
# > dining table (60): 0.9139987230300903    BoundingBox(0.005,0.662,0.373,0.987)    SegmentationMask (4032 X 3024)
# > chair (56): 0.8410733938217163   BoundingBox(0.439,0.601,0.654,0.855)    SegmentationMask (4032 X 3024)
# > chair (56): 0.8362091183662415   BoundingBox(0.556,0.549,0.702,0.736)    SegmentationMask (4032 X 3024)
# > vase (75): 0.5476816296577454    BoundingBox(0.486,0.415,0.504,0.441)    SegmentationMask (4032 X 3024)
# > potted plant (58): 0.5424181222915649    BoundingBox(0.464,0.389,0.507,0.442)    SegmentationMask (4032 X 3024)

```

### Project configuration YAML example:

```yaml
instance_segmentation:
    model_name: detectron2
    params:
        model_config: ../../../data/models/detectron2/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/mask_rcnn_R_50_FPN_3x.yaml
        model_weights: ../../../data/models/detectron2/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/model_final_f10217.pkl
        confidence_threshold: 0.5
        use_cuda: True
```

## Person Keypoint Detection

Models:

- keypoint_rcnn_R_50_FPN_3x:
  - ``data/models/detectron2/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x/model_final_a6e10b.pkl``
  - [https://dl.fbaipublicfiles.com/detectron2/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x/137849621/model_final_a6e10b.pkl](https://dl.fbaipublicfiles.com/detectron2/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x/137849621/model_final_a6e10b.pkl)
- keypoint_rcnn_X_101_32x8d_FPN_3x:
  - ``data/models/detectron2/COCO-Keypoints/keypoint_rcnn_X_101_32x8d_FPN_3x/model_final_5ad38f.pkl``
  - [https://dl.fbaipublicfiles.com/detectron2/COCO-Keypoints/keypoint_rcnn_X_101_32x8d_FPN_3x/139686956/model_final_5ad38f.pkl](https://dl.fbaipublicfiles.com/detectron2/COCO-Keypoints/keypoint_rcnn_X_101_32x8d_FPN_3x/139686956/model_final_5ad38f.pkl)

### Performance on [COCO](https://cocodataset.org) dataset
| Backbone | box AP| kp AP | Inference time (s/img) - CPU | Inference time (s/img) - GPU|
|-|-|-|-|-|
| keypoint_rcnn_R_50_FPN_3x | 55.4% | 65.5% | 11.4326 | 0.1099 |
| keypoint_rcnn_X_101_32x8d_FPN_3x | 57.3% | 66.0% | 12.6266 | 0.1316 |

<sup>**CPU:** Intel(R) Xeon(R) Silver 4116 || **GPU:** Quadro RTX 8000</sup>

### Usage example

```python
import cv2
from toolbox.Models.detectron2 import Detectron2

img = cv2.imread("data/samples/images/general/person_04.jpg")

detectron = Detectron2(
    model_config="data/models/detectron2/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x/keypoint_rcnn_R_50_FPN_3x.yaml",
    model_weights="data/models/detectron2/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x/model_final_a6e10b.pkl",
    use_cuda=False
)

instances = detectron.predict(img)

print(len(instances))
# > 1

print(instances[0].fields)
# > ['confidence', 'label_id', 'label', 'bounding_box', 'keypoints']

print(f"{instances[0].label} ({instances[0].label_id}): {instances[0].confidence} | {instances[0].bounding_box} | {instances[0].keypoints}")
# > person (0): 0.9998873472213745 | BoundingBox(0.306,0.048,0.710,0.998) | COCOKeypoints (17)

for name, kp in instances[0].keypoints.visible_keypoints.items():
    print(name, kp)
# > nose [0.5161009430885315, 0.11442655324935913, 1.7052081823349]
# > left_eye [0.5302745699882507, 0.09819693118333817, 2.926452159881592]
# > right_eye [0.4960910677909851, 0.10319066047668457, 0.9791648387908936]
# > left_ear [0.5519519448280334, 0.15187954902648926, 0.9948522448539734]
# > right_ear [0.4735800325870514, 0.1656123399734497, 2.0866847038269043]
# > left_shoulder [0.5652918219566345, 0.3316539227962494, 0.2762047052383423]
# > right_shoulder [0.4635750651359558, 0.28421348333358765, 0.2031673938035965]
# > left_elbow [0.5386120080947876, 0.5363969802856445, 0.4380788803100586]
# > right_elbow [0.48024994134902954, 0.4564972519874573, 1.0254446268081665]
# > left_wrist [0.5878028869628906, 0.6799668073654175, 0.6801812052726746]
# > right_wrist [0.6186513900756836, 0.49020496010780334, 1.079840898513794]
# > left_hip [0.4510689377784729, 0.686208963394165, 0.12466149777173996]
# > right_hip [0.3693620562553406, 0.6537497043609619, 0.08254873752593994]
# > left_knee [0.5861353874206543, 0.9146721959114075, 0.30979645252227783]
# > right_knee [0.41271671652793884, 0.9446346759796143, 0.37432464957237244]
# > left_ankle [0.4177192151546478, 0.9945720434188843, 0.061957959085702896]
# > right_ankle [0.3418485224246979, 0.9945720434188843, 0.08313897252082825]
```

### Project configuration YAML example:

```yaml
keypoints:
    model_name: detectron2
    params:
        model_config: ../../../data/models/detectron2/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x/keypoint_rcnn_R_50_FPN_3x.yaml
        model_weights: ../../../data/models/detectron2/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x/model_final_a6e10b.pkl
        confidence_threshold: 0.5
        use_cuda: True
```
