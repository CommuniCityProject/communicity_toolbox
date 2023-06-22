# Machine learning models

This page lists the provided machine learning models that are pre-trained and ready to use for inference. The weights of the models are located by default in ``data/models/`` and can be downloaded from the [GitHub releases](https://github.com/CommuniCityProject/communicity_toolbox/releases).

The output of the models is composed of [Toolbox Structures](./structures.md).

## Face analysis
| Name | Description | Output |
|------|-------------|--------|
| [age_gender](../toolbox/Models/age_gender/README.md) | Predict the age and gender of a face image | ([Gender](https://communicity-docs.readthedocs.io/en/latest/docs/toolbox/Structures.html#Structures.Gender.Gender), float)
| [emotions_hse](../toolbox/Models/emotions_hse/README.md) | Recognize 7 different emotions from a face image | [Emotion](https://communicity-docs.readthedocs.io/en/latest/docs/toolbox/Structures.html#module-Structures.Emotion)
| [face_recognition_facenet](../toolbox/Models/face_recognition_facenet/README.md) | Perform face recognition tasks | (str, float) \| np.ndarray

## Object detection

| Name | Description | Output |
|------|-------------|--------|
| [face_detector_retinaface](../toolbox/Models/face_detector_retinaface/README.md) | Detect faces in images | [BoundingBox](https://communicity-docs.readthedocs.io/en/latest/docs/toolbox/Structures.html#module-Structures.BoundingBox)
| [face_detector_ultraface](../toolbox/Models/face_detector_ultraface/README.md) | Detect faces in images | [BoundingBox](https://communicity-docs.readthedocs.io/en/latest/docs/toolbox/Structures.html#module-Structures.BoundingBox)

## Instance segmentation

| Name | Description | Output |
|------|-------------|--------|
| [detectron2](../toolbox/Models/detectron2/README.md) | Perform instance segmentation of 80 different objects | [SegmentationMask](https://communicity-docs.readthedocs.io/en/latest/docs/toolbox/Structures.html#module-Structures.SegmentationMask)

## Keypoints

| Name | Description | Output |
|------|-------------|--------|
| [detectron2](../toolbox/Models/detectron2/README.md) | Predict the position of 17 body key points | [COCOKeypoints](https://communicity-docs.readthedocs.io/en/latest/docs/toolbox/Structures.html#module-Structures.Keypoints)
