# Detectron2

[Detectron2](https://github.com/facebookresearch/detectron2) is a library that provides state-of-the-art detection and segmentation algorithms implemented in [PyTorch](https://pytorch.org/).

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
| mask_rcnn_X_101_32x8d_FPN_3x | 44.3% | 39.5% |  |  |

<sup>**CPU:** Intel(R) Xeon(R) Silver 4116 || **GPU:** Quadro RTX 8000</sup>

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
| keypoint_rcnn_X_101_32x8d_FPN_3x | 57.3% | 66.0% |  |  |

<sup>**CPU:** Intel(R) Xeon(R) Silver 4116 || **GPU:** Quadro RTX 8000</sup>