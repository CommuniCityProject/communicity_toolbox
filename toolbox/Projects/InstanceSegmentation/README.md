# Instance Segmentation

This Project aims to detect and segment objects in images.

![instance segmentation](/docs/res/instance_segmentation.jpg)

## Data models

This project uses the [InstanceSegmentation](/docs/DataModels/InstanceSegmentation/) data model.

## Configuration

This project uses a configuration YAML with the following fields:

- ``instance_segmentation``:  Specifies the name and parameters of the instance segmentation model. It must have the following fields:
  - ``model_name``:  Name of the model.
  - ``params``:  The parameters of the models' python class.
- ``context_broker``:
    - ``host``:  IP address of the Context Broker
    - ``port``:  Port of the Context Broker
    - ``notification_uri``:  URI where the subscription notifications will be sent
- ``api``:
    - ``host``:  Bind IP address of the API server
    - ``port``:  Bind port of the API server
    - ``allowed_origins``: List of origins that should be permitted to make cross-origin requests
    - ``local_image_storage``: Flags if the images are stored locally and can be accessed by their path or must be retrieved from a URL
- ``subscriptions``:  List of subscriptions to create on the context broker. Each element can have the following fields:
    - ``entity_type``:  Entity type to subscribe to
    - ``watched_attributes``:  List of attributes to subscribe to
    - ``query``:  Query to filter the entities to subscribe to

<details>
<summary>Example:</summary>

```
instance_segmentation:
  model_name: detectron2
  params:
    model_config: ../../../data/models/detectron2/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/mask_rcnn_R_50_FPN_3x.yaml
    model_weights: ../../../data/models/detectron2/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/model_final_f10217.pkl
    confidence_threshold: 0.5
    use_cuda: True

context_broker:
  host: 192.168.0.100
  port: 1026
  notification_uri: http://192.168.0.100:8080/ngsi-ld/v1/notify

api:
  host: 0.0.0.0
  port: 8080
  allowed_origins: []
  local_image_storage: True

subscriptions:
  - entity_type: Image
    watched_attributes: ["purpose"]
    query: "purpose==%22InstanceSegmentation%22"
```

</details>


## API

The API allows the Project to be executed as a service. It has automatic and interactive documentation generated with [swagger-ui](https://github.com/swagger-api/swagger-ui) on ``/docs`` and [redoc](https://github.com/Redocly/redoc) on ``/redoc``.

### Endpoints

- **``GET``** _/_

    Returns the name and version of the API

    - **Response**

      <details>
      <summary>application/json</summary>

      ```
      {
        "title": "Instance Segmentation API",
        "version": "0.2.0"
      }
      ```

    </details>

- **``POST``** _/predict_

    Predict bounding boxes and masks of the objects in an image. It returns a list of data models for each detected object. The response type can be specified with the ``accept`` header (``application/json`` or ``application/ld+json``)

    - **Request body**

      A json with the following fields:

      - ``entity_id``:  The id of an image entity in the context broker to perform instance segmentation on
      - ``post_to_broker``:  Flag if the generated data models should be posted to the context broker. Defaults to ``true``
    
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
      - ``type``:  The type of the data model (``InstanceSegmentation``)
      - ``image``:  The id of the source image entity
      - ``mask``:  The mask of the object in the image (RLE compressed binary mask with hexadecimal encoding)
      - ``boundingBox``:  The bounding box of the object in the image with relative image coordinates
      - ``confidence``:  The confidence of the detection
      - ``label``:  The label of the detected object
      - ``labelId``:  The label id of the detected object

      </br>
      <details>
      <summary>application/json</summary>

      ```
      [
        {
          "id": "string",
          "dateObserved": "string",
          "type": "InstanceSegmentation",
          "image": "string",
          "mask": {
            "size": [integer, integer],
            "counts": "string"
          },
          "boundingBox": {
            "xmin": number,
            "ymin": number,
            "xmax": number,
            "ymax": number
          },
          "label": "number",
          "labelId": integer,
          "confidence": number
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
          "type": "InstanceSegmentation",
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
          "mask": {
            "type": "Property",
            "value": {
              "size": [integer, integer],
              "counts": "string"
            }
          },
          "boundingBox": {
            "type": "Property",
            "value": {
              "xmin": number,
              "ymin": number,
              "xmax": number,
              "ymax": number
            }
          },
          "label": {
            "type": "Property",
            "value": "string"
          },
          "labelId": {
            "type": "Property",
            "value": integer
          },
          "confidence": {
            "type": "Property",
            "value": number
          }
        }
      ]
      ```
      </details>

- **``POST``** _/ngsi-ld/v1/notify_
  
  Route to notify the activation of a subscription (usually used by a context broker)

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