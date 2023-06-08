
# HSEmotion

HSEmotion (High-Speed face Emotion recognition) is a model that performs facial emotion recognition, distinguishing between 7 different expressions.

It is implemented in [TensorFlow](https://www.tensorflow.org). The official code can be found [here](https://github.com/HSE-asavchenko/face-emotion-recognition).

Weights are available in the [releases](https://github.com/CommuniCityProject/communicity_toolbox/releases) section of the repository:
- mobilenet_7.h5: ``data/models/emotions_hse/mobilenet_7.h5``

### Performance on [AffectNet](http://mohammadmahoor.com/affectnet/) dataset (7 classes)

| Backbone | Accuracy | Inference time (s/img) - CPU | Inference time (s/img) - GPU|
|-|-|-|-|
| mobilenet_7 | 64.71 | 0.0782 | 0.0742 |

<sup>**CPU:** Intel(R) Xeon(R) Silver 4116 || **GPU:** Quadro RTX 8000</sup>

### Usage example

```python
import cv2
from toolbox.Models.emotions_hse import EmotionsClassifier

img = cv2.imread("data/samples/images/faces/emotions/ffhq_215.png")

model = EmotionsClassifier(
    model_path="data/models/emotions_hse/mobilenet_7.h5", 
    use_cuda=False
)
instances = model.predict(img)

print(len(instances))
# > 1

print(instances[0].fields)
# > ['emotion', 'confidence']

print(f"{instances[0].emotion} ({type(instances[0].emotion)}): {instances[0].confidence}")
# > HAPPINESS (<enum 'Emotion'>): 0.9740390181541443
```

### Project configuration YAML example:

```yaml
face_emotions:
  model_name: emotions_hse
  params:
    model_path: ../../../data/models/emotions_hse/mobilenet_7.h5
    use_cuda: False
```
