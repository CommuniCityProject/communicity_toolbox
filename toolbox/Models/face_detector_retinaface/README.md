# RetinaFace

RetinaFace is a single-stage face detector implemented on [PyTorch](https://pytorch.org/) based on the original paper ['RetinaFace: Single-stage Dense Face Localisation in the Wild'](https://arxiv.org/abs/1905.00641).

The official code can be found [here](https://github.com/biubug6/Pytorch_Retinaface).

Weights are available in the [releases](https://github.com/CommuniCityProject/communicity_toolbox/releases) section of the repository:
- Resnet50: ``data/models/face_detector_retinaface/mobilenet0.25_Final.pth``
- Mobilenet0.25: ``data/models/face_detector_retinaface/Resnet50_Final.pth``

### Performance on WIDER Face Val dataset

| Backbone | AP - easy | AP - medium | AP - hard | Inference time (s/img) - CPU | Inference time (s/img) - GPU|
|-|-|-|-|-|-|
| Resnet50 | 95.48% |94.04% | 84.43% | 0. | 0.037 |
| Mobilenet0.25 | 90.70% | 88.16% | 73.82% | 0. | 0. |

<sup>**CPU:** Intel(R) Xeon(R) Silver 4116 || **GPU:** Quadro RTX 8000</sup>

### Usage example

```

```

### Project configuration YAML example:

```

```

<details>
<summary>Note:</summary>

The model may struggle to detect large faces since it was trained with anchors of sizes from ~16 to ~512 pixels. To solve this issue, use the parameter ``max_input_size`` to scale down larger images (for example to ``512``).
    
</details>