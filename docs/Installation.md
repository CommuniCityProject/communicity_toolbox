# Installation

Requirements:
- Python [3.9 - 3.10]

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

3. Install the toolbox package and its requirements

    ```
    python -m pip install -r requirements.txt
    python -m pip install -e .
    ```

