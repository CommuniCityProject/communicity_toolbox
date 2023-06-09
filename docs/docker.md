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

2. Download the Toolbox's data from the repository [releases](https://github.com/CommuniCityProject/communicity_toolbox/releases), which includes machine learning models and additional resources. Download and extract it manually or run the following script:
    
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

It will also mount a volume on the ``/home/user/communicity_toolbox/data`` path, that will be bound to the host's ``toolbox/data`` path. This allow the Toolbox components to access the machine learning models and configurations on the host machine.

To enable GPU support, add the argument: ``--gpus all``

## Use Docker Compose

A [Docker Compose file](../docker-compose.yaml) is provided to run all the Toolbox Project APIs.

It also includes an Orion-LD context broker instance, required by the Toolbox services. If you want to use your own context broker, remove the ``orion`` and ``mongo-db`` services and the ``mongo-db`` volume. Then change the fields ``x-common-env: BROKER_HOST`` and ``x-common-env: BROKER_PORT`` to point to your context broker.

The ``x-common-env: HOST`` field should be changed to the address of the machine where the services will run.

In the ``volumes`` section are defined the file system volumes that will be mounted on each container. Most services have a volume bound to the ``data`` host directory, so configuration files and machine learning models can be shared among services and the host. Also, another volume is created to share the uploaded images to the ImageStorage service. This allows other services to access images directly from the disk.

The default configuration files used by the Projects are located in the ``data/configs/`` directory. You can modify these files to edit the parameters of each service.

- To set up Docker Compose, run in the Toolbox root directory:
    ```
    docker compose up
    ```
