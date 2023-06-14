# Docker guide

This guide shows how to use the Toolbox with Docker.

Requirements:
- Git
- Docker
- Optional GPU support: CUDA >=10.1 

## Clone the repository

First of all, download the Toolbox repository and the required data:

1. Clone the repository and navigate to the project directory.

    ```
    git clone https://github.com/CommuniCityProject/communicity_toolbox.git
    cd communicity_toolbox
    ```

2. Download the Toolbox's data from the repository [releases](https://github.com/CommuniCityProject/communicity_toolbox/releases), which includes machine learning models and additional resources. Download and extract it manually inside ``communicity_toolbox/`` or run the following script:
    
    ```
    python download_data.py
    ```

## Get the Toolbox Docker image

We provide a Docker image with the Toolbox and all its requirements already installed. This image can be downloaded from the [docker hub](https://hub.docker.com/r/egracia/toolbox) or built from the source code:

### Use an already-built Docker image

Use ``docker pull`` to download the image from the CommuniCity Docker hub: [https://hub.docker.com/r/egracia/toolbox/tags](https://hub.docker.com/r/egracia/toolbox/tags):


### Build the image from source

Build the image with the provided [Dockerfile](../Dockerfile).
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

It will also mount a volume on the ``/home/user/communicity_toolbox/data`` path, which will be bound to the host's ``toolbox/data`` path. This allows the Toolbox components to access the machine learning models and configurations on the host machine.

To enable GPU support, add the argument: ``--gpus all``

## Use Docker Compose

A [Docker Compose file](../docker-compose.yaml) is provided to run all the Toolbox Project APIs on different ports.

- Prerequisites:

    The Toolbox components require access to a context broker. The recommended one is [Orion-LD](https://github.com/FIWARE/context.Orion-LD). It can be launched using the provided Docker compose file ([docker/orion-ld.yaml](../docker/orion-ld.yaml)):
    ```
    docker compose -f docker/orion-ld.yaml up -d
    ```

1. Edit the ``docker-compose.yaml`` file. Change the ``x-common-env: HOST`` field to the address of the machine where the services will run. This address will be used by the context broker to send notifications to the APIs. If needed, also change the fields ``x-common-env: BROKER_HOST`` and ``x-common-env: BROKER_PORT`` to point to your context broker. The field ``USE_CUDA`` can be used to enable GPU usage by the machine learning models.

    The ``volumes`` section defines the file system volumes that will be mounted on each container. Most services have a volume bound to the ``data`` host directory, so configuration files and machine learning models can be shared among services and the host machine. Also, another volume is created to share the uploaded images to the ImageStorage service. This allows other services to access images directly from the disk.

    The default configuration files used by the Projects are located in the ``data/configs/`` directory. You can modify these files to edit each service's parameters.

2. Set up Docker Compose by running on the repository root directory:
    ```
    docker compose up
    ```
