# Image Storage

This Project offers a REST API server to store and retrieve images, as well as visualize the generated Toolbox data models. It keeps track of the images on a context broker so other applications can access and reference them.

### Motivation

The Toolbox Projects APIs typically require an image as input. To facilitate this, this service offers common image storage for uploading and accessing images.

Since a context broker is not intended for storing large files, this service instead stores images in a local folder and maintains a reference to them in the context broker via the _[Image](https://github.com/CommuniCityProject/communicity_toolbox/tree/master/docs/DataModels/Image)_ data model.

### Overview

When an image is uploaded a URL-safe, secure and random id is generated. This id is returned as a response and it can be used to retrieve back the image. An entity is created with some metadata about the image on the context broker, with the same id, following the _[Image](https://github.com/CommuniCityProject/communicity_toolbox/tree/master/docs/DataModels/Image)_ data model. This data model includes a URL that can be used to retrieve the image, a path to the image file that can be used by applications running on the same machine and some metadata about the image, such as its size.

The API also includes a route to visualize the Toolbox data models which draws its content to the source image. It also accepts the visualization parameters, such as colors, font size or image size. When a data model is visualized, a new image is created and its id is returned as a response which can then be used to retrieve the image. This id is a hash of the data models and the visualization parameters, so the same calls will return the same image/id.

This API also allows limiting the type and size of the uploaded images as well as the storage size. The size, type and integrity of the images are checked for each upload. It is also possible to limit the maximum number of image files, the total storage size and the time the images are stored. When this limit is exceeded, the oldest images are deleted.

## Data models

This project uses the _[Image](https://github.com/CommuniCityProject/communicity_toolbox/tree/master/docs/DataModels/Image)_ data model.

## Configuration

This project uses a configuration YAML with the following fields:

- ``context_broker``:
    - ``host``: IP address of the Context Broker.
    - ``port``: Port of the Context Broker.
- ``api``:
    - ``host``: Bind IP address of the API server.
    - ``port``: Bind port of the API server.
    - ``allowed_origins``: List of origins that should be permitted to make cross-origin requests.
    - ``external_url``: URL of the API server. It is used to generate the URLs of the images.
    - ``ngsild_urn``: URN of the image entities on the Context Broker. It must contain a ``{}`` where the image id will be placed.
    - ``allowed_mime``: List of allowed MIME types for the uploaded images.
    - ``max_upload_size``: Maximum size of uploaded files in bytes. Set to null to disable.
    - ``storage_path``: Path where save the images. It must be writable by the user running the API server.
    - ``delete_from_broker``: If true, the image entities are deleted from the Context Broker when the images are deleted from the storage.
    - ``cleanup_on_end``: If true, all the images are deleted when the API server is stopped.
    - ``max_n_files``: Maximum number of files in the storage path. If reached, the oldest files will be deleted. Set to null to disable.
    - ``max_dir_size``: Maximum size of the storage directory in bytes. If reached, the oldest files will be deleted. Set to null to disable.
    - ``max_file_time``: Maximum amount of seconds a file can exist. If a file was created more than ``max_file_time`` seconds ago, it will be deleted. Set to null to disable.
    - ``update_time``: When using ``max_file_time``, the creation time of files will be checked periodically every ``update_time`` seconds.
    - ``allow_uploads``: If true, the API allows uploading images.
    - ``allow_entity_visualization``: If true, the API allows the visualization of the Toolbox data models.
    - ``max_entities_visualize``: Maximum allowed number of entities to visualize in one single image. Set to null to disable.

<details>
<summary>Example:</summary>

```
context_broker:
  host: 192.168.0.100
  port: 1026  

api:
  host: 0.0.0.0
  port: 8080
  external_url: http://192.168.0.100:8080/
  ngsild_urn: "urn:ngsi-ld:Image:{}"
  allowed_origins: []
  allowed_mime:
    - image/png
    - image/jpeg
    - image/JPEG
    - image/bmp
    - image/jp2
    - image/tiff
  max_upload_size: 10e6
  storage_path: /home/user/toolbox/storage
  delete_from_broker: True
  cleanup_on_end: False
  max_n_files: 1e3
  max_dir_size: 10e9
  max_file_time: 2.592e+6 # 30 days
  update_time: 86400 # 1 day
  allow_uploads: True
  allow_entity_visualization: True
  max_entities_visualize: 100
```

</details>

## API

The [swagger-ui](https://github.com/swagger-api/swagger-ui) documentation is available on ``/docs`` and the [redoc](https://github.com/Redocly/redoc) version on ``/redoc``.

### Endpoints

- **``GET``** _/_

    Get an image by its id.

     - **Query parameters**
    
        ``image_id``: The id of an image.

    - **Response**

      An image.

    </details>

- **``POST``** _/_
    
    Upload an image.
    
    This route is only available if ``allow_uploads`` is set to ``true``.

    - **Request body**

        A multipart/form-data with the following data:

        - ``file``: An image file.
        - ``source``: Optional source of the image (NGSI id or text). It will be set on the context broker data model.
        - ``purpose``: Optional purpose of the image if any. It will be set on the context broker data model.

    - **Response**

        The id of the image.

- **``POST``** _/visualize_
    
    Visualize the data of one or more Toolbox data models from the context broker.

    This route is only available if ``allow_entity_visualization`` is set to ``true``.
    
    - **Request body**

        A JSON with the following fields:

        - ``entity_ids``: A list of entity ids to visualize in one single image. All the entities must have the same source image, which will be used as background.
        - ``params``: Optional object with the visualization parameters.

    - **Response**
    
      The id of the generated image, which can be retrieved with a ``GET`` request to ``/``.
      Multiple calls to this endpoint with the same parameters will return the same image id.