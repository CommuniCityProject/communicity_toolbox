# Machine learning models

This page lists the provided machine learning models that are pre-trained and ready to use for inference. Toolbox Models are located under [toolbox/Models/](/toolbox/Models/). The weights files are available on the [GitHub releases]().

## Face analysis
| Name | Description | Weights | CPU inference time (s) | Output |
|------|-------------|---------|------------------------|--------|
| [age_gender](/toolbox/Models/age_gender/) | Predict the age and gender of facial images | age_model.onnx <br/> gender_model.onnx | Age + Gender: 0.318 <br/> Age: 0.164 <br/> Gender: 0.157 | ([Gender](/toolbox/Structures/Gender.py), float)
| [emotions_hse](/toolbox/Models/emotions_hse/) | Classify 7 different emotions from a face image | mobilenet_7.h5 | 0.059 | [Emotion](/toolbox/Structures/Emotion.py)
| [face_recognition_facenet](/toolbox/Models/face_recognition_facenet/) | Perform face recognition | squeezenet_VGGFace2 | 0.019 | (str, float) \| np.ndarray

## Object detection

| Name | Description | Weights | CPU inference time (s) | Output |
|------|-------------|---------|------------------------|--------|
| [face_detector_retinaface](/toolbox/Models/face_detector_retinaface/) | Detect faces on images | Resnet50_Final.pth | 0.722 |  [BoundingBox](/toolbox/Structures/BoundingBox.py)
| [face_detector_retinaface](/toolbox/Models/face_detector_retinaface/) | Detect faces on images | mobilenet0.25_Final.pth | 0.071 | [BoundingBox](/toolbox/Structures/BoundingBox.py)
| [face_detector_mtcnn](/toolbox/Models/face_detector_mtcnn/) | Detect faces on images | mtcnn.pb | 0.042 | [BoundingBox](/toolbox/Structures/BoundingBox.py)
| [face_detector_ultraface](/toolbox/Models/face_detector_ultraface/) | Detect faces on images | version-RFB-320.onnx | 0.014 | [BoundingBox](/toolbox/Structures/BoundingBox.py)
| [face_detector_ultraface](/toolbox/Models/face_detector_ultraface/) | Detect faces on images | version-RFB-640.onnx | 0.043 | [BoundingBox](/toolbox/Structures/BoundingBox.py)

## Instance segmentation

| Name | Description | Weights | CPU inference time (s) | Output |
|------|-------------|---------|------------------------|--------|
| [detectron2](/toolbox/Models/detectron2/) | Perform instance segmentation of 80 different objects | mask_rcnn_R_50_FPN_3x | 2.259 | [SegmentationMask](/toolbox/Structures/SegmentationMask.py)

## Keypoints

| Name | Description | Weights | CPU inference time (s) | Output |
|------|-------------|---------|------------------------|--------|
| [detectron2](/toolbox/Models/detectron2/) | Predict the position of 17 body key points | keypoint_rcnn_R_50_FPN_3x | 2.263 | [COCOKeypoints](/toolbox/Structures/Keypoints.py)

<sub>*CPU inference time is the average time taken to predict a black image of size 512x512, on an Intel(R) Xeon(R) CPU E5-1620 v4 </sup>