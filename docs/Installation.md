# Installation guide

This guide shows how to manually install the Toolbox and its requirements as a Python package.

Requirements:
- Python [3.9 - 3.10]
- Optional for GPU support: CUDA >=10.1

1. Clone the repository and navigate to the project directory

    ```
    git clone https://github.com/CommuniCityProject/communicity_toolbox.git
    cd communicity_toolbox
    ```

2. The machine learning models and some additional resources are available in the repository [releases](https://github.com/CommuniCityProject/communicity_toolbox/releases), on a _data.zip_ file. To download and extract it run:
    
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

3. Install the Python requirements

    ```
    python -m pip install -r requirements.txt
    ```

4. Install Detectron2

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
Some Toolbox components require an NGSI-LD context broker to function. The recommended one is [Orion-LD](https://github.com/FIWARE/context.Orion-LD). You can launch an instance with Docker Compose using the provided [docker-compose](https://github.com/CommuniCityProject/communicity_toolbox/blob/master/Orion-LD.yaml) file.

Requirements:
- docker-compose

```
docker compose -f Orion-LD.yaml up -d
```
