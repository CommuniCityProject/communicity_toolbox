# Facenet 

Facenet is a face recognition model implemented in [TensorFlow](https://www.tensorflow.org), based on the original paper ["FaceNet: A Unified Embedding for Face Recognition and Clustering"](https://arxiv.org/abs/1503.03832).

The official code can be found [here](https://github.com/davidsandberg/facenet).

Weights are available in the [releases](https://github.com/CommuniCityProject/communicity_toolbox/releases) section of the repository:
- squeezenet_VGGFace2: ``data/models/face_recognition_facenet/squeezenet_VGGFace2/model-20180204-160909.*``

### Performance on [LFW](http://vis-www.cs.umass.edu/lfw/) dataset

| Model | Accuracy | Inference time (s/img) - CPU | Inference time (s/img) - GPU|
|-|-|-|-|
| squeezenet_VGGFace2 | 98.2% | 0. | 0. |

<sup>**CPU:** Intel(R) Xeon(R) Silver 4116 || **GPU:** Quadro RTX 8000</sup>

### Usage example

```python

```

### Project configuration YAML example:

```yaml

```
