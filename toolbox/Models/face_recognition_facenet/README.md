# Facenet 

Facenet is a face recognition model implemented in [TensorFlow](https://www.tensorflow.org), based on the original paper ["FaceNet: A Unified Embedding for Face Recognition and Clustering"](https://arxiv.org/abs/1503.03832).

The official code can be found [here](https://github.com/davidsandberg/facenet).

Weights are available in the [releases](https://github.com/CommuniCityProject/communicity_toolbox/releases) section of the repository:
- squeezenet_VGGFace2: ``data/models/face_recognition_facenet/squeezenet_VGGFace2/model-20180204-160909.*``

### Performance on [LFW](http://vis-www.cs.umass.edu/lfw/) dataset

| Model | Accuracy | Inference time (s/img) - CPU | Inference time (s/img) - GPU|
|-|-|-|-|
| squeezenet_VGGFace2 | 98.2% | 0.03542 | 0.0331 |

<sup>**CPU:** Intel(R) Xeon(R) Silver 4116 || **GPU:** Quadro RTX 8000</sup>

### Usage example

```python
import cv2
from toolbox.Models.face_recognition_facenet import FaceRecognition

img = cv2.imread("data/samples/images/faces/celeb_single/urn;ngsi-ld;Person;Elton_John.jpg")
img_flip = cv2.flip(img, 1)

# Load the face recognition models
recognition = FaceRecognition(
    model_path="data/models/face_recognition_facenet/squeezenet_VGGFace2/model-20180204-160909.ckpt-266000",
    use_cuda=False
)
recognition.load_model()

instances = recognition.recognize_image(img)
print(instances)
# > []

features = recognition.predict_features(img)
print(type(features), features.shape, features.dtype)
# > <class 'numpy.ndarray'> (128,) float32

recognition.add_features("elton_john", features)

instances = recognition.recognize_image(img_flip)
print(len(instances), instances[0].fields)
# > 1 ['name', 'distance']

print(instances[0].name, instances[0].distance)
# > elton_john 0.07795006

```

### Project configuration YAML example:

```yaml
face_recognition:
    model_name: face_recognition_facenet
    params:
        distance_threshold: 0.75
        model_path: ../../../data/models/face_recognition_facenet/squeezenet_VGGFace2/model-20180204-160909.ckpt-266000
        use_cuda: True
```
