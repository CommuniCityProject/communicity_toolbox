# Docker guide

This guide shows how to use the Toolbox with Docker.

Requirements:
- Docker
- Optional for GPU support: CUDA >=10.1 

## Clone the repository

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

## Get the Toolbox Docker image

We provide a Docker image with the Toolbox and all its requirements already installed. This image can be downloaded from the [docker hub](https://hub.docker.com/r/egracia/toolbox) or built from the source code:

### Use an already-built Docker image

A Toolbox image can be pulled from the CommuniCity Docker hub. Refer to [https://hub.docker.com/r/egracia/toolbox/tags](https://hub.docker.com/r/egracia/toolbox/tags) to get the latest version.

Use ``docker pull`` to download the desired image.

### Build the image from source

The Docker image can be also built with the [Dockerfile]() provided in the Toolbox repository. It will install the Toolbox from the current source code.

Use this method to get the latest version of the Toolbox or to install your own modified version.

Inside the Toolbox repository, run:
```
docker build -t toolbox .
```

## Run the toolbox on a Docker container

To use the Toolbox in a development environment or execute it with command lines, create a Docker container from the existing Toolbox image.

```
docker run -it -v <path_to_the_toolbox>/data:/home/user/communicity_toolbox/data -p 8080:8080 --name test_toolbox toolbox bash
```
This will create a Docker container, named ``test_toolbox``, from the image named ``toolbox`` and will launch a bash shell. The image name may vary if you pulled the image from the docker hub.

It will also mount a volume on the ``/home/user/communicity_toolbox/data`` path, that will be bound to the host's ``toolbox/data`` path. This allow the Toolbox components to access the machine learning models and configurations on the host machine.

To enable GPU support, add the argument: ``--gpus all``

## Use Docker compose

Docker compose can be used to run multiple containers with different services at once.
A [Docker compose file](../docker-compose.yaml) is provided to run each one of the Toolbox Project APIs.

First, edit the following fields on the ``docker-compose.yaml`` file:
- ``x-common-env: BROKER_HOST``: The context broker IP address.
- ``x-common-env: BROKER_PORT``: The context broker port.
- ``x-common-env: HOST``: The address of the machine where the services will run.

The ``services`` section defines the containers that will be created. Here is created one for each Toolbox Project, and its API is served on different ports.

In the ``volumes`` section are defined the file system volumes that will be mounted on each container. Most of the services have a volume bound to the ``data`` host directory, so the configuration files and machine learning models can be shared among services and the host. Also, another volume is created to share the uploaded images to the ImageStorage service. This allows other services to directly access the images from the disk.

The default configuration files used by the projects are located in the ``data/configs/`` directory. You can modify these files to edit the parameters of each service.

- Run the services:
    ```
    docker compose up
    ```
