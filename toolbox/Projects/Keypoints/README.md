# Keypoints

This Project aims to detect body keypoints in images. Keypoints are the location of some body parts such as elbows, wrists or knees. This allows us to get an estimation of the pose of a person in a given image.

![keypoints detection](/docs/res/keypoints.jpg)

## Data models

This project uses the [PersonKeyPoints](/docs/DataModels/PersonKeyPoints/) data model.

## Configuration

This project uses a configuration YAML with the following fields:

- ``keypoints``:  Specifies the name and parameters of the Keypoints detector model. It must have the following fields:
  - ``model_name``:  Name of the model.
  - ``params``:  The parameters of the models' python class.
- ``context_broker``:
    - ``host``:  IP address of the Context Broker
    - ``port``:  Port of the Context Broker
    - ``notification_uri``:  URI where the subscription notifications will be sent
- ``api``:
    - ``host``:  Bind IP address of the API server
    - ``port``:  Bind Port of the API server
    - ``allowed_origins``: List of origins that should be permitted to make cross-origin requests
    - ``local_image_storage``: Flags if the images are stored locally and can be accessed by their path or must be retrieved from a URL
- ``subscriptions``:  List of subscriptions to create on the context broker. Each element can have the following fields:
    - ``entity_type``:  Entity type to subscribe to
    - ``watched_attributes``:  List of attributes to subscribe to
    - ``query``:  Query to filter the entities to subscribe to

<details>
<summary>Example:</summary>

```
keypoints:
  model_name: detectron2
  params:
    model_config: ../../../data/models/detectron2/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x/keypoint_rcnn_R_50_FPN_3x.yaml
    model_weights: ../../../data/models/detectron2/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x/model_final_a6e10b.pkl
    confidence_threshold: 0.5
    use_cuda: False

context_broker:
  host: 192.168.0.100
  port: 1026
  # URI where notifications will be sent
  notification_uri: http://192.168.0.100:8080/ngsi-ld/v1/notify

api:
  host: 0.0.0.0
  port: 8080
  
  # List of origins that should be permitted to make cross-origin requests.
  allowed_origins: []
  
  # If the images are stored locally and can be accessed by their path.
  local_image_storage: False

subscriptions:
  - entity_type: Image
    watched_attributes: ["purpose"]
    query: "purpose==%22Keypoints%22"
```

</details>


## API

The API allows to execute the Project as a service. It has automatic and interactive documentation generated with [swagger-ui](https://github.com/swagger-api/swagger-ui) on ``/docs`` and [redoc](https://github.com/Redocly/redoc) on ``/redoc``.

### Endpoints

- **``GET``** _/_

    Returns the name and version of the API

    - **Response**

      <details>
      <summary>application/json</summary>

      ```
      {
        "title": "Keypoints API",
        "version": "0.2.0"
      }
      ```

    </details>

- **``POST``** _/predict_

    Predict the keypoints of the persons in an image. It returns a list of data models with the keypoints of each person. The response type can be specified with the ``accept`` header (``application/json`` or ``application/ld+json``)

    - **Request body**

      A json with the following fields:

      - ``entity_id``:  The id of an image entity in the context broker to predict the keypoints of
      - ``post_to_broker``:  Flag if the generated data models should be posted to the context broker. Defualts to ``true``
    
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
    
      A list with the generated data models (one for each person) with the following fields:

      - ``id``:  The id of the entity on the context broker
      - ``dateObserved``:  The date when the data model was generated
      - ``type``:  The type of the data model (``PersonKeyPoints``)
      - ``image``:  The id of the source image entity
      - ``boundingBox``:  The bounding box of the person in the image with relative image coordinates
      - ``confidence``:  The confidence of the detection
      - ``keypoints``:  The keypoints of the person in the image where each keypoint is a list of three elements (``[x, y, confidence]``) and the coordinates are relative to the image size

      </br>
      <details>
      <summary>application/json</summary>

      ```
      [
        {
          "id": "string",
          "dateObserved": "string",
          "type": "PersonKeyPoints",
          "image": "string",
          "boundingBox": {
            "xmin": number,
            "ymin": number,
            "xmax": number,
            "ymax": number
          },
          "confidence": number,
          "keypoints": {
            "nose": [number, number, number],
            "left_eye": [number, number, number],
            "right_eye": [number, number, number],
            "left_ear": [number, number, number],
            "right_ear": [number, number, number],
            "left_shoulder": [number, number, number],
            "right_shoulder": [number, number, number],
            "left_elbow": [number, number, number],
            "right_elbow": [number, number, number],
            "left_wrist": [number, number, number],
            "right_wrist": [number, number, number],
            "left_hip": [number, number, number],
            "right_hip": [number, number, number],
            "left_knee": [number, number, number],
            "right_knee": [number, number, number],
            "left_ankle": [number, number, number],
            "right_ankle": [number, number, number]
          }
        }
      ]
      ```
      </details>
    
      <details>
      <summary>application/ld+json</summary>

      ```
      [
        {
          "id": "string",
          "type": "PersonKeyPoints",
          "@context": [],
          "dateObserved": {
            "type": "Property",
            "value": {
              "@type": "DateTime",
              "@value": "string"
            }
          },
          "image": {
            "type": "Relationship",
            "object": "string"
          },
          "boundingBox": {
            "type": "Property",
            "value": {
              "xmin": number
              "ymin": number
              "xmax": number
              "ymax": number
            }
          },
          "confidence": {
            "type": "Property",
            "value": number
          },
          "keypoints": {
            "type": "Property",
            "value": {
              "nose": [number, number, number],
              "left_eye": [number, number, number],
              "right_eye": [number, number, number],
              "left_ear": [number, number, number],
              "right_ear": [number, number, number],
              "left_shoulder": [number, number, number],
              "right_shoulder": [number, number, number],
              "left_elbow": [number, number, number],
              "right_elbow": [number, number, number],
              "left_wrist": [number, number, number],
              "right_wrist": [number, number, number],
              "left_hip": [number, number, number],
              "right_hip": [number, number, number],
              "left_knee": [number, number, number],
              "right_knee": [number, number, number],
              "left_ankle": [number, number, number],
              "right_ankle": [number, number, number]
            }
          }
        }
      ]
      ```
      </details>

- **``POST``** _/ngsi-ld/v1/notify_
  
  It is used by the context broker to notify the activation of a subscription.

  - **Query parameters**
    
    ``subscriptionId``: The id of the subscription

  - **Request body**

      A json with the following fields:

      - ``id``:  The id of the notification
      - ``type``:  ``Notification``
      - ``subscriptionId``:  The id of the subscription
      - ``notifiedAt``:  The date when the notification was sent
      - ``data``:  A list with the entities notified
    
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

    ``204`` if the notification was processed successfully