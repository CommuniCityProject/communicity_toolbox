# Ubuntu 18.04 | cuda 11.2 | cudnn 8 | Python 3.9 | tensorflow 2.7.0 | torch 1.8.1 | detectron2
FROM nvidia/cuda:11.2.0-cudnn8-devel-ubuntu18.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y curl git wget ninja-build nano sudo ca-certificates build-essential zip

# Create a non-root user
ARG USER_ID=1000
RUN useradd -m --no-log-init --system --uid ${USER_ID} user -g sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER user
WORKDIR /home/user

# Enable color prompt
RUN sed -i '/#force_color_prompt=yes/c\force_color_prompt=yes' /home/user/.bashrc

# Install Python 3.9
RUN sudo DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common
RUN sudo add-apt-repository --yes ppa:deadsnakes/ppa
RUN sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3.9 python3.9-distutils python3.9-dev python3.9-venv
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.9
RUN export PATH=/home/user/.local/bin:$PATH

# Change the default python version
RUN sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1
RUN sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
RUN sudo update-alternatives --set python /usr/bin/python3.9
RUN sudo update-alternatives --set python3 /usr/bin/python3.9

# Install dependencies
RUN python -m pip install --upgrade pip
RUN python -m pip install --upgrade setuptools
COPY ./requirements.txt /home/user/requirements.txt
RUN python -m pip install -r /home/user/requirements.txt

# Install detectron2
RUN python -m pip install --user 'git+https://github.com/facebookresearch/fvcore'
RUN git clone https://github.com/facebookresearch/detectron2 detectron2
RUN git -C detectron2 checkout tags/v0.6
ENV FORCE_CUDA="1"
ARG TORCH_CUDA_ARCH_LIST="Kepler;Kepler+Tesla;Maxwell;Maxwell+Tegra;Pascal;Volta;Turing"
ENV TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST}"
RUN python -m pip install --user -e detectron2
ENV FVCORE_CACHE="/tmp"

# Install the toolbox
RUN sudo mkdir -p /var/communicity_toolbox/image_storage
RUN sudo mkdir /etc/communicity_toolbox
RUN sudo chown -R user /var/communicity_toolbox
RUN sudo chown -R user /etc/communicity_toolbox
ENV TOOLBOX="/home/user/communicity_toolbox"
ENV XDG_CACHE_HOME="/etc/communicity_toolbox/models/torch_cache"
RUN mkdir /home/user/communicity_toolbox
COPY ./toolbox/ /home/user/communicity_toolbox/toolbox
COPY ./setup.py/ /home/user/communicity_toolbox
RUN chown user /home/user/communicity_toolbox
WORKDIR /home/user/communicity_toolbox
RUN python -m pip install -e .