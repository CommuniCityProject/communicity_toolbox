# Toolbox Structures

The Toolbox Structures are a set of Python Classes used to represent the output of machine learning algorithms.

The following Structures are implemented:

## [Instance](https://github.com/CommuniCityProject/communicity_toolbox/blob/master/toolbox/Structures/Instance.py)

Structure similar to a Python ``dict``, used to aggregate the different outputs of a machine learning algorithm for each instance.
e.g. A face detector algorithm will produce an ``Instance`` object for each detected face, storing inside it the bounding box and the detection confidence.

```Python
from toolbox.Structures import Instance
instance = Instance().set("label", "Car").set("confidence", 0.99)
print(instance.fields)
# > ['label', 'confidence']
print(instance.label)
# > 'Car'
print(dict(instance))
# > {'label': 'Car', 'confidence': 0.99}
```

## [BoundingBox](https://github.com/CommuniCityProject/communicity_toolbox/blob/master/toolbox/Structures/BoundingBox.py)

Used to store the coordinates of a bounding box, that is a set of two points delimiting a rectangular area that encloses an object in an image. By default it uses the minimum and maximum x and y coordinates, which represents the top-left and bottom-right corner of the object inside the image. The coordinates of the bounding box are relative to the image size, ranging from ``0.`` to ``1.``.

```Python
from toolbox.Structures import BoundingBox
box = BoundingBox(xmin=0.1, ymin=0.2, xmax=0.5, ymax=0.8)
print(box, box.get_width(), box.get_height(), box.get_area())
# > BoundingBox(0.1,0.2,0.5,0.8) 0.4 0.6 0.24
```

## [Emotion](https://github.com/CommuniCityProject/communicity_toolbox/blob/master/toolbox/Structures/Emotion.py)

``Enum`` class used to define the expression of a face.

Defined values: ``(ANGER, DISGUST, FEAR, HAPPINESS, NEUTRAL, SADNESS, SURPRISE)``

```Python
from toolbox.Structures import Emotion
print(Emotion.HAPPINESS)
# > HAPPINESS
```

## [Gender](https://github.com/CommuniCityProject/communicity_toolbox/blob/master/toolbox/Structures/Gender.py)

``Enum`` class used to define the gender of a person.

Defined values: ``(FEMALE, MALE, OTHER)``

```Python
from toolbox.Structures import Gender
print(Gender.FEMALE)
# > FEMALE
```

## [Image](https://github.com/CommuniCityProject/communicity_toolbox/blob/master/toolbox/Structures/Image.py)

Structure to store an image, allowing to load it from a local file or an URL.

```Python
from toolbox.Structures import Image
image = Image("data/samples/images/general/house_00.jpg")
print(image.width, image.height, type(image.image))
# > 4032 3024 <class 'numpy.ndarray'>

image = Image("http://via.placeholder.com/640x360")
print(image.image.shape)
# > (360, 640, 3)
```

## [Keypoints](https://github.com/CommuniCityProject/communicity_toolbox/blob/master/toolbox/Structures/Keypoints.py)

Store a set of keypoints that represents the position of some body parts in an image. The coordinates are relative to the image size.

```Python
import numpy as np
from toolbox.Structures.Keypoints import COCOKeypoints

keypoints = COCOKeypoints(np.random.random((17,3)))
print(keypoints.visible_keypoints)
# > {'nose': [0.25174146084934534, 0.41149472947613597, 0.4136625103019802],
#  'left_eye': [0.5149775330854244, 0.8652653090649927, 0.2548453786275874],
#  'right_eye': [0.9657882949253714, 0.6916385617510773, 0.3114271499589921],
#  'left_ear': [0.431570059641474, 0.6737029372539967, 0.8450525204479465],
#  'right_ear': [0.63588555756413, 0.6859269636416803, 0.7640058043587045],
#  'left_shoulder': [0.9901896493790687, 0.013833551968123081, 0.7126951678248445],
#  'right_shoulder': [0.8442300146807435, 0.6279988367180737, 0.9988792028321307],
#  'left_elbow': [0.09529990865784699, 0.42516585488034897, 0.8767336772714116],
#  'right_elbow': [0.2206766690296298, 0.6494975278635126, 0.8052212593200703],
#  'left_wrist': [0.5866653003971699, 0.9700380507147964, 0.7066035570368658],
#  'right_wrist': [0.1497427895450849, 0.563088417393093, 0.29788679462560685],
#  'left_hip': [0.36789137614995704, 0.5423404370943875, 0.812699563487156],
#  'right_hip': [0.9066483138008675, 0.2514379588310641, 0.6042841971323476],
#  'left_knee': [0.9721808496816008, 0.7659541569894651, 0.4340997622861066],
#  'right_knee': [0.4831249787665922, 0.7833441940908007, 0.5898400316687347],
#  'left_ankle': [0.653796012176348, 0.38935338870211633, 0.9559334567680202],
#  'right_ankle': [0.7277946288755803, 0.90788956211731, 0.4920530598870443]}
```

## [SegmentationMask](https://github.com/CommuniCityProject/communicity_toolbox/blob/master/toolbox/Structures/SegmentationMask.py)

Represents a segmentation mask, that is a binary image defining the region occupied by an object in an image.

```Python
import numpy as np
from toolbox.Structures import SegmentationMask

mask = np.zeros((100,100), dtype=bool)
mask[:50, 50:] = True
segmentation = SegmentationMask(mask=mask)

print(segmentation.width, segmentation.height, segmentation.area, type(segmentation.mask))
# > 100 100 2500 <class 'numpy.ndarray'>

print(segmentation.rle)
# > {'size': [100, 100], 'counts': b'Xl4b1b100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'}
```
