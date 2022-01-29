#!/bin/bash

# Ask for administrator password up front
sudo -v

# Keep-alive: update existing `sudo` timestamp until script is finished
while true; do sudo -=n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# Install latest versions of curl, git, and python3(-dev)
sudo apt-get update 
sudo apt-get install curl git python3 python3-dev

## Install Gaussian16

while true 
do
  read -p -r "Would you like to configure the server for Gaussian16[yN]?: " conf_gauss

  conf_gauss="${conf_gauss:=n}"
  case $conf_gauss in
    [yY][eE][sS]|[yY])
      # Create g16 user group, take ownership of $GAUSS_SCRDIR, $g16root/g16 folders
      sudo groupadd g16
      sudo chgrp -R g16 /usr/bin/g16
      sudo chgrp -R g16 /scratch-data/g16-scratch
      
      # Export Gaussian information to skeleton .profile if it's not present
      if ! (grep -q "g16root" /etc/skel/.profile); then
        sudo cat <<- EOF >> /etc/skel/.profile
					## Bash setup commands for g16
					export g16root="/usr/bin"
					export GAUSS_SCRDIR="/scrach-data/g16-scratch"

					source $g16root/g16/bsd/g16.profile
				EOF
      fi
    ;;
    [nN][oO]|[nN])
      echo "You said no, resuming installation"
    ;;
    *)
      echo "Invalid input, please choose [Y]es or [N]o"
    ;;
  esac
done

## Install The Littlest JupyerHub

# Download and install TLJH
# TODO: create requirements file with packages required in base environment? Need to pass as URL
curl -L https://tljh.jupyter.org/bootstrap.py | sudo -E python3 - \
  --user-requirements-txt-url \
  https://raw.githubusercontent.com/mskblackbelt/Chem357/main/Server%20setup/pchem2-requirements.txt

## Set up system for HTTPS access
# Create certificate/key pair for authentication
key_file="/etc/ssl/private/sugarcube.key"
cert_file="/etc/ssl/certs/sugarcube.crt"
sudo openssl req -x509 -nodes -days 9999 -newkey rsa:2048 -keyout "$key_file" -out "$cert_file"

# Add TLJH binaries to the PATH
export PATH=/opt/tljh/user/bin:${PATH}

# Modify tljh/user.py to add specific skel folder and groups to new users, reformat with `black`
user_file="/opt/tljh/hub/lib/python3.8/site-packages/tljh/user.py"
sudo sed -i "s/\(\"--create-home\"\)/\1, \"--skel \/etc\/skel-tljh\", \"--groups gaussian\"/" "$user_file"
sudo /opt/tljh/user/bin/black "$user_file"

## Create skeleton user folder for new JupyterHub users
sudo cp /etc/skel /etc/skel-tljh

sudo mkdir -p /srv/shared/{data,submissions}



sudo ln -s /srv/shared /etc/skel-tljh
sudo ln -s /srv/data /etc/skel-tljh

## Configure TLJH via tljh-config

# Enable NativeAuthenticator to create new Linux users
sudo tljh-config set auth.type nativeauthenticator.NativeAuthenticator

# Check users passwords against a common list for more security
sudo tljh-config set c.Authenticator.check_common_password True

# Make JupyterLab the default interface
sudo tljh-config set user_environment.default_app jupyterlab

# Prompt for admin username for TLJH
read -p "Enter admin user(s) for TLJH (separate users with a space): " users
# Add administrator user(s)
sudo tljh-config add-item users.admin $users

# Set limits for CPU cores and memory use
sudo tljh-config set limits.cpu 4
sudo tljh-config set limits.memory 3G
# Set idle timeout period to 30 minutes
sudo tljh-config set services.cull.timeout 1800

# Set up HTTPS settings for TLJH
sudo tljh-config set https.enabled true
sudo tljh-config set https.port 443
sudo tljh-config set https.tls.key "$key_file"
sudo tljh-config set https.tls.cert "$cert_file"

# Set up notebook templates
template_dir="/opt/tljh/user/share/jupyter/notebook_templates"
sudo tljh-config set c.JupyterLabTemplates.template_dirs "$template_dir"


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

# Restart TLJH and Traefik on completion
sudo service jupyterhub restart
sudo service traefik restart