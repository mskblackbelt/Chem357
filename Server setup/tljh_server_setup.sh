#!/bin/bash

export PATH=/opt/tljh/user/bin:$PATH

# Ask for administrator password up front
sudo -v

# Keep-alive: update existing `sudo` timestamp until script is finished
while true; do sudo -=n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# Install latest versions of curl, git, and python3(-dev)
sudo apt-get update 
sudo apt-get install curl git python3 python3-dev

## Install The Littlest JupyerHub

# Download and install TLJH
# TODO: create requirements file with packages required in base environment? Need to pass as URL
curl -L https://tljh.jupyter.org/bootstrap.py | sudo -E python3 - 

# TODO: modify tljh/user.py to add specific skel folder and groups to new users
sudo sed -i s/("--create-home")/$1, "--skel /etc/skel-tljh", "--groups gaussian"/ /opt/tljh/??

## Configure TLJH via tljh-config

# Enable NativeAuthenticator to create new Linux users
sudo tljh-config set auth.type nativeauthenticator.NativeAuthenticator

# Make JupyterLab the default interface
sudo tljh-config set user_environment.default_app jupyterlab

# Prompt for admin username for TLJH
read -p "Enter admin user(s) for TLJH: " users
# Add administrator user(s)
sudo tljh-config add-item users.admin $users



# TODO: upgrade mamba, pip, conda to latest versions?
# TODO: check location of mamba binary
# sudo /opt/tljh/user/bin/mamba upgrade -y mamba conda pip

# TODO: Install packages in base conda environment (if not implemented during installation)

# Install computation conda env (prompt for file path first)
read -p "Location of environment.yml file: " env_file_loc
sudo /opt/tljh/user/bin/conda env create -f="$env_file_loc"

# TODO: Install jupyterlab extension for OpenChemistry (need to know location of conda binary… or activate conda env?)

# Configure JupyterLab templates
sudo /opt/tljh/user/bin/jupyter serverextension enable --py jupyterlab_templates

# TODO: place desired templates in appropriate location

# TODO: give access to the new python kernel for pchem users
sudo /opt/tljh/user/bin/python3 -m ipython kernel install --name "pchem2" --display-name "Python (PChem Lab)" --sys-prefix

## Create skeleton user folder for new JupyterHub users

sudo cp /etc/skel /etc/skel-tljh

sudo mkdir -p /srv/shared/{data,submissions}



sudo ln -s /srv/shared /etc/skel-tljh
sudo ln -s /srv/data /etc/skel-tljh

## Install Gaussian16

# Create g16 user group, take ownership of $GAUSS_SCRDIR, $g16root/g16 folders
# Export Gaussian information to skeleton .profile
sudo cat << EOF >> /etc/skel-tljh/.profile
## Bash setup commands for g16
export g16root="/usr/bin" 
export GAUSS_SCRDIR="/scrach-data/g16-scratch"

source $g16root/g16/bsd/g16.profile
EOF

# Restart TLJH and Traefik on completion
sudo service jupyterhub restart
sudo service traefik restart