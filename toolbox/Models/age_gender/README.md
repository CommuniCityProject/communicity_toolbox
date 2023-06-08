
# AgeGender

AgeGender are two DCNN models trained to infer the age and gender of a face image.

Weights are available in the [releases](https://github.com/CommuniCityProject/communicity_toolbox/releases) section of the repository:
- age_model.onnx: ``data/models/age_gender/age_model.onnx``
- gender_model.onnx: ``data/models/age_gender/gender_model.onnx``

### Performance

| Model | Inference time (s/img) - CPU |
|-|-|
| age_model | 0.1896 |
| gender_model | 0.1719 |

<sup>**CPU:** Intel(R) Xeon(R) Silver 4116</sup>

### Usage example

```python
import cv2
from toolbox.Models.age_gender import AgeGenderPredictor

img = cv2.imread("data/samples/images/faces/celeb/mindy_kaling/0.jpg")

model = AgeGenderPredictor(
    age_model_path="data/models/age_gender/age_model.onnx",
    gender_model_path="data/models/age_gender/gender_model.onnx"
)
instances = model.predict(img)

print(len(instances))
# > 1

print(instances[0].fields)
# > ['age', 'gender', 'gender_confidence']

print(f"{instances[0].age} | {instances[0].gender} ({type(instances[0].gender)}): {instances[0].gender_confidence}")
# > 38.11524963378906 | FEMALE (<enum 'Gender'>): 0.989403486251831
```

### Project configuration YAML example:

```yaml
age_gender:
    model_name: age_gender
    params:
        age_model_path: ../../../data/models/age_gender/age_model.onnx
        gender_model_path: ../../../data/models/age_gender/gender_model.onnx
        do_age: True
        do_gender: True
```
