# Docker

First of all download the toolbox project and its data:

1. Clone the repository and navigate to the project directory.

    ```
    git clone https://github.com/edgarGracia/communicity_toolbox.git
    cd communicity_toolbox
    ```

2. The machine learning models and some additional resources are available in the repository releases, on a _data.zip_ file. To download and extract it just run the _download_data_ script:

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

To run the toolbox inside a container, first build the Docker image:

```
docker build -t toolbox .
```

Then create a container from the toolbox image. For example:

```
docker run -it -v <path_to_the_toolbox>/data:/home/user/communicity_toolbox/data -p 8080:8080 --gpus all --name toolbox toolbox bash
```

## Use Docker compose

Docker compose can be used to run multiple containers with different toolbox components at once.
A [Docker compose file](/docker-compose.yaml) is provided to run each one of the toolbox Project APIs.

First edit the following fields on the [docker-compose.yaml](docker-compose.yaml) file:
- ``x-common-env: BROKER_HOST``: the context broker address.
- ``x-common-env: BROKER_PORT``: the context broker port.
- ``x-common-env: HOST``: the address of the machine where the services will run.

The default configuration files used by the projects are located on the ``data/configs/`` directory.

Set up docker compose with:
```
docker compose up
```
