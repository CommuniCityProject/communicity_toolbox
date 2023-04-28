# Toolbox installation

This guide shows how to manually install the Toolbox and its requirements on a Linux machine with optional GPU support.

Requirements:
- Python [3.9 - 3.10]
- Optional for GPU support: CUDA >=10.1 

1. Clone the repository and navigate to the project directory

    ```
    git clone https://github.com/CommuniCityProject/communicity_toolbox.git
    cd communicity_toolbox
    ```

2. The machine learning models and some additional resources are available in the repository releases, on a _data.zip_ file. To download and extract it run:
    
    ```
    bash ./download_data.sh
    ```

3. Install the Python requirements

    ```
    python -m pip install -r requirements.txt
    ```

4. Install Detectron2

    <!-- <details>
    <summary>Optional GPU support:</summary>
        
        export FORCE_CUDA="1"
        export TORCH_CUDA_ARCH_LIST="Kepler;Kepler+Tesla;Maxwell;Maxwell+Tegra;Pascal;Volta;Turing"
        export TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST}"
    </details> -->

    ```
    python -m pip install --user 'git+https://github.com/facebookresearch/fvcore'
    git clone https://github.com/facebookresearch/detectron2 detectron2
    python -m pip install --user -e detectron2
    ```

5. Install the Toolbox

    ```
    python -m pip install -e .
    ```

## Optional: Install Orion-LD
Some Toolbox components require an NGSI-LD context broker to work. The recommended one is [Orion-LD](https://github.com/FIWARE/context.Orion-LD). You can install it by following the next steps:

Requirements:
- docker-compose

1. Create a folder named _orion-ld_ and navigate to it

    ```
    mkdir orion-ld
    cd orion-ld
    ```

2. Create a file named _docker-compose.yaml_ with the following content:
    ```
    version: "3.5"
    services:
      orion:
        image: fiware/orion-ld:1.1.0
        hostname: orion
        restart: always
        container_name: fiware-orion
        depends_on:
          - mongo-db
        expose:
          - "1026"
        ports:
          - "1026:1026" 
        command: -dbhost mongo-db -logLevel DEBUG
        healthcheck:
          test: curl --fail -s http://orion:1026/version || exit 1
      mongo-db:
        image: mongo:4.0
        hostname: mongo-db
        container_name: db-mongo
        expose:
          - "27017"
        ports:
          - "27017:27017" 
        command: --nojournal
        volumes:
          - mongo-db:/data
    volumes:
      mongo-db: ~
    ```

3. Run docker compose

    ```
    docker compose up -d
    ```
