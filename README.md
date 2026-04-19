# Kconfig Documentation Using ConfiGen

## Requirements
- Operating system: Linux (Ubuntu 22.04 LTS)
- Packages: flex bison make cmake git curl unzip python3 python3-pip python3-venv python3-setuptools python3-dev

## Using ConfiGen in Ubuntu 22.04 LTS

### Install Requirements
- Open a terminal
- `sudo apt update`
- `sudo apt install -y flex bison make cmake git cscope`
- `sudo apt install -y python3 python3-pip python3-venv python3-setuptools python3-dev`
- `sudo apt install -y curl nano unzip`
- Install `git-lfs`
    - `curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash`
    - `sudo apt install git-lfs`
    - `git lfs install`
- `mkdir configen_workspace`
- `cd configen_workspace`

### Setup Virtual Environment
- `python3 -m venv .venv`
- `source .venv/bin/activate`

### Install ConfiGen
- `git clone https://github.com/JobayerAhmmed/ConfiGen.git`
- `cd ConfiGen/doxygen`
- `mkdir build && cd build`
- `cmake -G "Unix Makefiles" ..`
- `sudo make install`
- `cd ../../..`

### Install kextractor
- `git clone -b kextract --single-branch https://github.com/JobayerAhmmed/kmax.git`
- `cd kmax`
- `python3 setup.py install`
- `cd ..`

### Generate documentation for a project (BusyBox)
- Download BusyBox (you can choose BusyBox version, we chose v1.36.0)
    - `curl -O https://busybox.net/downloads/busybox-1.36.0.tar.bz2`
- Unzip
    - `tar -xvf busybox-1.36.0.tar.bz2`
    - `cd busybox-1.36.0`
- Copy ConfiGen configuration file
    - `cp ../ConfiGen/Doxyfile_bbox ./Doxyfile`
- Copy and run shell script to generate Config.in files
    - `cp ../ConfiGen/gen_config_files_bbox.sh .`
    - `chmod 744 gen_config_files_bbox.sh`
    - `./gen_config_files_bbox.sh .`
- Run ConfiGen
    - `doxygen`
- Open file *ConfiGen/busybox-1.36.0/doxygen_doc/html/index.html*
    in a browser and you will find the generated documentation.


# Commit Analysis
For commit analysis, read [here](commit_parser/README.md).

# Acknowledgments
This work was funded in part by the National Science Foundation, CNS-2234908,
CNS-2234909, CCF-1941816, and CCF-1909688.
Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author and do not necessarily reflect the views of the National Science Foundation.
