# Age Gender

This Project aims to detect faces in images and infer their age and gender.

![age gender](../../../docs/res/age_gender.jpg)

## Data models

This project uses the _[Face](https://github.com/CommuniCityProject/communicity_toolbox/tree/master/docs/DataModels/Face)_ data model.

## Configuration

This project uses a configuration YAML with the following fields:

- ``age_gender``:  Specifies the name and parameters of the age and gender models. It must have the following fields:
    - ``model_name``:  Name of the model.
    - ``params``:  The parameters of the models' python class.
- ``face_detector``: Specifies the name and parameters of the face detector model. It must have the following fields:
    - ``face_box_scale``: Scale factor to apply to the face bounding box.
    - ``model_name``:  Name of the model.
    - ``params``:  The parameters of the models' python class.
- ``context_broker``:
    - ``host``:  IP address of the Context Broker.
    - ``port``:  Port of the Context Broker.
    - ``notification_uri``:  URI where the subscription notifications will be sent.
    - ``check_subscription_conflicts``: Flag if the subscription conflicts should be checked before creating them.
- ``api``:
    - ``host``:  Bind IP address of the API server.
    - ``port``:  Bind port of the API server.
    - ``allowed_origins``: List of origins that should be permitted to make cross-origin requests.
    - ``local_image_storage``: Flags if the images are stored locally and can be accessed by their path or must be retrieved from a URL.
    - ``post_new_entity``: Create a new _Face_ entity in the context broker with the predicted age and gender when processing a _Face_ entity.
    - ``update_entity``: Update the _Face_ entity in the context broker with the predicted age and gender when processing a _Face_ entity.
- ``subscriptions``:  List of subscriptions to create on the context broker. Each element can have the following fields:
    - ``entity_type``:  Entity type to subscribe to.
    - ``watched_attributes``:  List of attributes to subscribe to.
    - ``query``:  Query to filter the entities to subscribe to.

<details>
<summary>Example:</summary>

```
age_gender:
  model_name: age_gender
  params:
    age_model_path: ../../../data/models/age_gender/age_model.onnx
    gender_model_path: ../../../data/models/age_gender/gender_model.onnx
    do_age: True
    do_gender: True
    use_cuda: False

face_detector:
  face_box_scale: 1.2
  model_name: face_detector_retinaface
  params:
    weights_path: ../../../data/models/face_detector_retinaface/Resnet50_Final.pth
    model_name: resnet50
    confidence_threshold: 0.7
    landmarks: False
    nms_threshold: 0.4
    use_cuda: False

context_broker:
  host: 192.168.0.100
  port: 1026
  notification_uri: http://192.168.0.100:8080/ngsi-ld/v1/notify
  check_subscription_conflicts: True

api:
  host: 0.0.0.0
  port: 8080
  allowed_origins: []
  local_image_storage: True
  post_new_entity: False
  update_entity: True

subscriptions:
  - entity_type: Image
    watched_attributes: ["purpose"]
    query: "purpose==%22AgeGender%22"
```

</details>

## API

The API allows the Project to be executed as a service. It has automatic and interactive documentation generated with [swagger-ui](https://github.com/swagger-api/swagger-ui) on ``/docs`` and [redoc](https://github.com/Redocly/redoc) on ``/redoc``.

### Endpoints

- **``GET``** _/_

    Returns the name and version of the API.

    - **Response**

      <details>
      <summary>application/json</summary>

      ```
      {
        "title": "Age Gender API",
        "version": "0.2.0"
      }
      ```

    </details>

- **``POST``** _/predict_
    
    If an image entity is provided, it predicts the position (bounding box) of faces in the image and estimates their age and gender. If a _Face_ entity is provided, it uses the existing bounding box to get an image of the face and estimate its age and gender.
    
    It returns a list of data models for each detection. The response type can be specified with the ``accept`` header (``application/json`` or ``application/ld+json``).

    - **Request body**

        A JSON with the following fields:

        - ``entity_id``:  The id of an image or a _Face_ entity in the context broker to estimate its age end gender.
        - ``post_to_broker``:  Flag if the generated data models should be posted to the context broker. Defaults to ``true``.

        </br>
        <details>
        <summary>application/json</summary>

        ```
        {
          "entity_id": "string",
          "post_to_broker": true
        }
        ```

        </details>

    - **Response**
    
      A list with the generated data models (one for each face) with the following fields:

      - ``id``:  The id of the entity on the context broker.
      - ``dateObserved``:  The date when the data model was generated.
      - ``type``:  The type of the data model (``Face``).
      - ``image``:  The id of the source image entity.
      - ``boundingBox``:  The bounding box of the face in the image with relative image coordinates.
      - ``detectionConfidence``:  The confidence of the detection.
      - ``age``:  The estimated age of the face.
      - ``gender``:  The estimated gender of the face.
      - ``genderConfidence``:  The confidence of the gender classification.

      </br>
      <details>
      <summary>application/json</summary>

      ```
      [
        {
          "id": "urn:ngsi-ld:Face:b5dWqOszEe2iW7eYE~ARXw",
          "dateObserved": "2023-05-05T10:56:05.448390",
          "type": "Face",
          "image": "urn:ngsi-ld:Image:UXNVwGfrEQ74_fl7snsQLS71jdBshsE6fq8TR1gWBn4",
          "boundingBox": {
            "xmin": 0.66875,
            "ymin": 0.21481481481481482,
            "xmax": 0.7505208333333333,
            "ymax": 0.40185185185185185
          },
          "detectionConfidence": 0.9998043179512024,
          "age": 36.279388427734375,
          "gender": "FEMALE",
          "genderConfidence": 0.9704904556274414,
          "emotion": null,
          "emotionConfidence": null,
          "features": null,
          "featuresAlgorithm": null,
          "recognitionDomain": null,
          "recognized": false,
          "recognizedDistance": null,
          "recognizedPerson": null
        }
      ]
      ```
      </details>
    
      <details>
      <summary>application/ld+json</summary>

      ```
      [
        {
          "id": "urn:ngsi-ld:Face:wPoej~szEe2CS7eYE~ARXw",
          "type": "Face",
          "@context": [
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
          ],
          "dateObserved": {
            "type": "Property",
            "value": {
              "@type": "DateTime",
              "@value": "2023-05-05T10:58:21Z"
            }
          },
          "image": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:Image:UXNVwGfrEQ74_fl7snsQLS71jdBshsE6fq8TR1gWBn4"
          },
          "boundingBox": {
            "type": "Property",
            "value": {
              "xmin": 0.66875,
              "ymin": 0.21481481481481482,
              "xmax": 0.7505208333333333,
              "ymax": 0.40185185185185185
            }
          },
          "detectionConfidence": {
            "type": "Property",
            "value": 0.9998043179512024
          },
          "age": {
            "type": "Property",
            "value": 36.279388427734375
          },
          "gender": {
            "type": "Property",
            "value": "FEMALE"
          },
          "genderConfidence": {
            "type": "Property",
            "value": 0.9704904556274414
          },
          "recognized": {
            "type": "Property",
            "value": false
          },
          "dateModified": {
            "type": "Property",
            "value": {
              "@type": "DateTime",
              "@value": "2023-05-05T10:58:23Z"
            }
          },
          "dateCreated": {
            "type": "Property",
            "value": {
              "@type": "DateTime",
              "@value": "2023-05-05T10:58:23Z"
            }
          }
        }
      ]
      ```
      </details>

- **``POST``** _/ngsi-ld/v1/notify_
  
    Route to notify the activation of a subscription from a context broker.

    - **Query parameters**
    
        ``subscriptionId``: The id of the subscription.

    - **Request body**

        A JSON with the following fields:

        - ``id``:  The id of the notification.
        - ``type``:  ``Notification``.
        - ``subscriptionId``:  The id of the subscription.
        - ``notifiedAt``:  The date when the notification was sent.
        - ``data``:  A list with the entities notified.
    
      </br>
      <details>
      <summary>application/json</summary>

      ```
      {
        "id": "string",
        "type": "Notification",
        "subscriptionId": "string",
        "notifiedAt": "string",
        "data": []
      }
      ```

    </details>

  - **Response**

    ``204`` _no content_: If the notification was processed successfully.
    