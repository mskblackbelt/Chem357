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
      # Create g16 user group if g16 or gaussian group doesn't exist
      if [[ $(getent group {g16,gaussian} | wc -l ) -eq 0 ]]; then 
        gauss_group="g16"
        sudo groupadd "$gauss_group"
      else
        gauss_group=$(getent group {g16,gaussian} | cut -d: -f1)
      fi
      # Create, take ownership of $GAUSS_SCRDIR, $g16root/g16 folders
      if [[ -d /usr/bin/g16 ]]; then 
        g16root="/usr/bin"
      else 
        echo "Gaussian16 not installed in default location,"
        echo "please provide g16root[/usr/bin]:" 
        read g16root
      fi
      echo "Provide location of g16 scratch directory[/scrach-data/g16-scratch]: " 
      read GAUSS_SCRDIR
      GAUSS_SCRDIR="${GAUSS_SCRDIR:=/scrach-data/g16-scratch}"
      sudo chgrp -R g16 $g16root/g16
      sudo chgrp -R g16 $GAUSS_SCRDIR
      
      # Export Gaussian information to skeleton .profile
      if [[ $(grep -q -c "g16root" /etc/skel/.profile) -lt 1 ]]; then 
        sudo cat <<- EOF >> /etc/skel/.profile
					## Bash setup commands for Gaussian16
					export g16root="$g16root" 
					export GAUSS_SCRDIR="$GAUSS_SCRDIR"

					source $g16root/g16/bsd/g16.profile
				EOF
      fi
    ;;
    [nN][oO]|[nN])
      echo "You said no, skipping Gaussian setup and resuming installation"
    ;;
    *)
      echo "Invalid input, please choose [Y]es or [N]o"
    ;;
  esac
done

## Create skeleton user folder for new JupyterHub users
sudo cp /etc/skel /etc/skel-tljh

sudo mkdir -p /srv/shared/{data,submissions}

sudo ln -s /srv/shared /etc/skel-tljh
sudo ln -s /srv/data /etc/skel-tljh

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
gauss_group="${gauss_group:=$(getent group {g16,gaussian} | cut -d: -f1)}"
user_file="/opt/tljh/hub/lib/python3.8/site-packages/tljh/user.py"
sudo sed -i "s/\(\"--create-home\"\)/\1, \"--skel\", \"\/etc\/skel-tljh\", \"--groups\", \"$gauss_group\"/" "$user_file"
sudo /opt/tljh/user/bin/black "$user_file"

## Configure TLJH via tljh-config

# Enable NativeAuthenticator to create new Linux users
sudo tljh-config set auth.type nativeauthenticator.NativeAuthenticator

# Check users passwords against a common list for more security
sudo tljh-config set c.Authenticator.check_common_password True

# Make JupyterLab the default interface
sudo tljh-config set user_environment.default_app jupyterlab

# Prompt for admin username for TLJH
echo "Enter admin user(s) for TLJH (separate users with a space): " 
read users
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

# Upgrade mamba, pip, conda to latest versions
sudo /opt/tljh/user/bin/mamba upgrade -y mamba conda pip

# Configure JupyterLab templates
# Install node.js v.12
# Instructions from https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-ubuntu-20-04
curl -sL https://deb.nodesource.com/setup_12.x | sudo bash

# Enable Jupyter Lab and Server extensions
sudo /opt/tljh/user/bin/jupyter labextension install jupyterlab_templates
sudo /opt/tljh/user/bin/jupyter serverextension enable --py --sys-prefix jupyterlab_templates

# TODO: place desired templates in appropriate location
# Templates need to be organized in subfolders in the $template_dir

# Set up notebook templates
template_dir="/opt/tljh/user/share/jupyter/notebook_templates"
echo "Location of Jupyter templates folder: " 
read template_folder
sudo mkdir -p "$template_dir"
if [[ -d "$template_folder" ]]; then
  sudo cp "$template_folder" "$template_dir"
fi
sudo tljh-config set c.JupyterLabTemplates.template_dirs "$template_dir"

# Install computation conda env (prompt for file path first)
echo "Location of environment.yml file: " 
read env_file_loc
sudo /opt/tljh/user/bin/conda env create -f="$env_file_loc"

# Add conda commands to /etc/skel-tljh/.bashrc
sudo cat <<- EOF >> /etc/skel/.profile
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/opt/tljh/user/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
		eval "$__conda_setup"
else
		if [ -f "/opt/tljh/user/etc/profile.d/conda.sh" ]; then
				. "/opt/tljh/user/etc/profile.d/conda.sh"
		else
				export PATH="/opt/tljh/user/bin:$PATH"
		fi
fi
unset __conda_setup
# <<< conda initialize <<<
EOF
fi

# Install jupyterlab extension for OpenChemistry 
# TODO: don't hard-code path, or activate conda env?
sudo /opt/tljh/user/envs/pchem2_lab/bin/jupyter labextension install @openchemistry/jupyterlab

# Give access to the new python kernel for pchem users
# TODO: don't hard-code env name
sudo /opt/tljh/user/envs/pchem2_lab/bin/python3 -m ipykernel install --name "pchem2_lab" --display-name "Python (PChem Lab)" --prefix="/opt/tljh/user"

## Give JupyterHub users access to shared folders in /srv
submission_dir="/srv/shared/submissions"
data_dir="/srv/shared/data"

# Transfer ownership of submission_dir to jupyterhub-admins
sudo chgrp -R jupyterhub-admins $submission_dir
# set s(t)icky bit and setgid bit, let admins have full run, block all others.
sudo chmod 3770 $submission_dir

# Allow jupyterhub-users to view contents, add their own material to the directory
sudo setfacl -m g:jupyterhub-users:rwx $submission_dir
# Set default permissions for new files to only allow the owner to view files. 
sudo setfacl -d -m o::--- $submission_dir
sudo setfacl -d -m g:jupyterhub-users:--- $submission_dir # might not be necessary…

# Transfer ownership of data_dir to jupyterhub-admins
sudo chgrp -R jupyterhub-admins $data_dir
# set setgid bit, allow admins to have full run, block others.
sudo chmod 2775 $data_dir

# Restart TLJH and Traefik on completion
sudo service jupyterhub restart
sudo service traefik restart