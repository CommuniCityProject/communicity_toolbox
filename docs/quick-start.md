# Quick-Start

One of the main objectives of the Toolbox is to offer a set of computer vision ML models that can be used and accessed in three different ways:
- As a web page, using the provided front-end that allows any user to quickly try the main functionalities of the Toolbox.
- As a set of APIs that can be deployed with docker composes.
- As a Python library.

These components work in conjunction with a context broker which is used to store and retrieve data.

...

The first step is to install the Toolbox using ``pip`` or a Docker image.
Refer to the installation guides:
- [Python installation](./installation.md)
- [Docker guide](./docker.md)

As described in the previous guides you will also need to download additional data, which includes the machine-learning models and some sample images that are available in zip files on the Github _releases_ page.

...

<!-- 1. An image is uploaded to the ImageStorage service and its id is returned. Alternatively, an _Image_ entity with an URL to an image can be created manually in the Context Broker.
2. The API of a Project is called using the ID of the previously created image. The project will process the image and it will return a list of entities with the results. We can also find the entities created on the Context Broker with the id of the returned entities.
3. If we want to visualize the created entities we can use the ImageStorage service to create an image with their data drawn over the source image. It will return an id that can be used to retrieve the image from the ImageStorage service. -->


<!-- 
Context
 data models
 context cli
ML Models
Projects
Strucutres
Visaulization -->


<!--
Notebooks tutorials
-->



To learn more about the Toolbox's components you can refer to:
- [Projects](./projects.md)
- [Data models](./data-models.md)
- [Machine learning models](./machine-learning-models.md)
- [Structures](./structures.md)