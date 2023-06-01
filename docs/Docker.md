# Docker guide

This guide shows how to run the Toolbox with Docker.

Requirements:
- Docker
- Optional for GPU support: CUDA >=10.1 

1. Clone the repository and navigate to the project directory.

    ```
    git clone https://github.com/CommuniCityProject/communicity_toolbox.git
    cd communicity_toolbox
    ```

2. The machine learning models and some additional resources are available in the repository [releases](https://github.com/CommuniCityProject/communicity_toolbox/releases), on _data.zip_. To download and extract it just run the _download_data_ script:

    <details>
    <summary>Linux</summary>

    ```
    bash ./download_data.sh
    ```

    </details>
    <details>
    <summary>Windows</summary>

    ```
    ./download_data.bat
    ```
    
    </details>

</br>

## Run the toolbox on a Docker container

To run the toolbox inside a container, first, build the Docker image:

```
docker build -t toolbox .
```

Then create a container from the toolbox image.

With GPU support:

```
docker run -it -v <path_to_the_toolbox>/data:/home/user/communicity_toolbox/data -p 8080:8080 --gpus all --name toolbox toolbox bash
```

Without GPU:

```
docker run -it -v <path_to_the_toolbox>/data:/home/user/communicity_toolbox/data -p 8080:8080 --name toolbox toolbox bash
```

## Use Docker compose

Docker compose can be used to run multiple containers with different toolbox components at once.
A [Docker compose file](../docker-compose.yaml) is provided to run each one of the Toolbox Project APIs.

First, edit the following fields on the ``docker-compose.yaml`` file:
- ``x-common-env: BROKER_HOST``: The context broker IP address.
- ``x-common-env: BROKER_PORT``: The context broker port.
- ``x-common-env: HOST``: The address of the machine where the services will run.

The ``services`` section defines the containers that will be created. Here is created one for each Toolbox Project, and its API is served on different ports.

In the ``volumes`` section are defined the file system volumes that will be mounted on each container. Most of the services have a volume bound to the ``data`` host directory, so the configuration files and machine learning models can be shared among services and the host. Also, another volume is created to share the uploaded images to the ImageStorage service. This allows other services to directly access the images from the disk.

The default configuration files used by the projects are located in the ``data/configs/`` directory.

- Run the services:
    ```
    docker compose up
    ```
