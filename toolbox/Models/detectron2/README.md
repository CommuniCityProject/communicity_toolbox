# Detectron2

[Detectron2](https://github.com/facebookresearch/detectron2) is a library that provides state-of-the-art detection and segmentation algorithms implemented in [PyTorch](https://pytorch.org/).

The official code can be found [here](https://github.com/facebookresearch/detectron2).

Weights are available in the [releases](https://github.com/CommuniCityProject/communicity_toolbox/releases) section of the repository and online:


## Instance Segmentation

- mask_rcnn_R_50_FPN_3x:
  - ``data/models/detectron2/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/model_final_f10217.pkl``
  - [https://dl.fbaipublicfiles.com/detectron2/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl](https://dl.fbaipublicfiles.com/detectron2/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl)

### Performance on [COCO](https://cocodataset.org) dataset
| Backbone | box AP| mask AP | Inference time (s/img) - CPU | Inference time (s/img) - GPU|
|-|-|-|-|-|
| mask_rcnn_R_50_FPN_3x | 41.0% | 37.2% | 6.4292 | 0.0690 |

<sup>**CPU:** Intel(R) Xeon(R) Silver 4116 || **GPU:** Quadro RTX 8000</sup>