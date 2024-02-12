Todo: Turn this all into a shell/python script

## Personal items

Install 

- bat
- curl
- git
- python3, python3-dev
- rcm
- texlive
- zsh
- zsh-syntax-highlighting

Link

- /usr/bin/batcat /usr/bin/bat
- /usr/bin/python3 /usr/bin/python
- /usr/share/zsh-syntax-highlighting /usr/local/share/zsh-syntax-highlighting

## Install Gaussian

Gaussian install: <https://gaussian.com/g16/g16bin_install.pdf>

- Add group for gaussian (`g16`)
- Add scratch directory, set group ownership to gaussian group
- Add relevant lines to `.profile` or `.bash_profile` in `/etc/skel`

## Install JupyterHub via [The Littlest JupyterHub](https://tljh.jupyter.org/en/latest/install/custom-server.html)

- `curl -L https://tljh.jupyter.org/bootstrap.py | sudo -E python3 - --admin <admin_user_name>`
- TLJH settings
  - `sudo tljh-config set auth.type nativeauthenticator.NativeAuthenticator`
  - `sudo tljh-config set user_environment.default_app jupyterlab`
- Upgrade mamba (`sudo -E mamba upgrade --all`)
- Create new conda environment for notebook use
  - `sudo -E conda env create -f=/path/to/environment.yml`

### Python packages

Base environment

- pip
- jupyterlab>=3.2
# - ipython>=7.30
- jupyterlab_server>=2.1
- jupyterlab-latex>=3.1
- jupyterlab_templates>=0.3
# - pygments
- nbgitpuller
- jupyterlab-git
# - ipykernel
- numpy, scipy, matplotlib

P. Chem. environment (base env plus)

- anaconda 2021.11            ??
- seaborn, pandas
- cclib			conda-forge 
- ipympl			conda-forge     ??
- nmrglue		bioconda 
- xarray			conda-forge 
- avogadro		pypi 
- openchemistry	pypi 
- psi4      psi

Jupyter labextensions (inside p. chem. env)

- @openchemistry/jupyterlab

### Configuring jupyterLab_templates

After installing (via `pip` or `conda`), must be enabled as a server extension

```bash
jupyter serverextension enable --py jupyterlab_templates
```

Place the desired templates into a folder scanned by JupyterLab (check via `jupyter --paths`)

### Configuring available Jupyter kernels

Kernels should be manually added to Jupyter as follows:

```bash
ipython kernel install --name “data-science” --
```

### Skeleton user profile

- Add /etc/skel-tljh folder for TLJH users
- Modify /etc/skel/.profile with g18 commands
- Link to /srv/shared, /srv/data folders for shared data and submission locations
- Modify /opt/tljh/user.py and add the following to the `useradd` command
  - "--skel /etc/skel-tljh" 
  - "--groups gaussian"


The following is unnecessary if users are added to the "gaussian" group

- Add `jupyterhub-users` group to ACL permissions for Gaussian/g16 binary, scratch directory
  - `setfacl -R -m g:jupyterhub-users:rx <directory>`


===============================================================================

## DMZ Reverse Proxy setup

ICIT has provisioned a VM running RedHat for us. 

They request we do the following:

> Mateusz,
> 
> Our gateway server in the DMZ will be handling the initial traffic requests and will be the initial HTTPS component of the routing.  The gateway is built to communicate with other servers on the DMZ, so we'll be setting up a virtual server in the DMZ for you.  That server will be managed by you and you'll need to install and configure a load balancer/rev. proxy (e.g. nginx/traefik/apache) to accept traffic from the gateway and proxy on to your lab system.
> 
> The communication on the DMZ should be encrypted, so you'll need to generate a self-signed cert to install on whatever reverse proxy you intend to use.  The communication between your DMZ virtual server and the lab machine should also be encrypted, so you'll need a self-signed cert or a Let's Encrypt cert on the lab machine and configure Traefik to use it.
> 
> For the public address, we need a hostname to apply to this service (somehostname.hunter.cuny.edu) - do you have something in mind?
> 
> Also, the communication between the DMZ virtual server and your lab machine is normally blocked and will need to be enabled.  What we'll need to know is what port you need to connect to on the lab machine.  If you configure Traefik with the SSL cert by following the TLJH guide, then that would be 443.  But if you change it to something else, we'll need to know that.  Just confirm when you have decided and the traffic can be enabled between the two systems.
> 
> We'll let you know as soon as the virtual server is ready for you, along with the credentials to access it.
> 
> Thank you,
> Jacob Radford

The (seemingly) easiest guides use `nginx`. Using <https://www.redhat.com/sysadmin/setting-reverse-proxies-nginx> to get going. 

- Installed nginx using `dnf install nginx`
- Start nginx at startup with `sudo systemctl enable --now nginx`
	- Able to check availability with `curl localhost`
- *May* need to modify with SELinux permissions, as nginx only has access to ports 80 and 443 (HTTP, HTTPS)
	- SELinux blocks nginx from looking at cert file, blocks access to TCP socket 443

SElinux config script:

```bash
semanage import <<EOF
boolean -D
login -D
interface -D
user -D
port -D
node -D
fcontext -D
module -D
ibendport -D
ibpkey -D
permissive -D
boolean -m -1 httpd_can_network_connect
boolean -m -1 httpd_can_network_relay
boolean -m -1 httpd_graceful_shutdown
boolean -m -1 httpd_read_user_content
boolean -m -1 nis_enabled
boolean -m -1 virt_sandbox_use_all_caps
boolean -m -1 virt_use_nfs
EOF
```

Settings for nginx are located in `/etc/nginx/nginx.conf`. 

Contents of `nginx.conf`

```nginx
error_log /var/log/nginx/error.log;
events { }
http {
        include         mime.types;
        include         /etc/nginx/proxy.conf;
        default_type    application/octet-stream;
        sendfile        on;
        keepalive_timeout       65;

log_format wscombined '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    'upgrade:"$http_upgrade" '
                    'connection:"$http_connection" '
                    'sent-connection:"$sent_http_connection" '
                    '"$http_referer" "$http_user_agent"';

        server {
                listen 443 ssl;
                ssl_certificate         /etc/pki/tls/certs/sugarcube.ss-crt.pem;
                ssl_certificate_key     /etc/pki/tls/private/sugarcube.ss-key.pem;

                ssl_verify_client       off;
                # ssl_trusted_certificate       /etc/pki/tls/certs/ca-bundle.crt;

                access_log /var/log/nginx/access_log wscombined;
                #access_log /var/log/nginx/access_log combined;

                location /{
                        proxy_pass https://146.95.158.49:443/;
                        proxy_set_header        Host                    "sugarcube.hunter.cuny.edu";
                        proxy_redirect          default;
                        proxy_http_version 1.1;
                        proxy_set_header Upgrade $http_upgrade;
                        proxy_set_header Connection "upgrade";
                        proxy_set_header X-Scheme "https";
                        proxy_set_header origin $http_origin;
                        proxy_set_header Sec-WebSocket-Key $http_sec_websocket_key;
                        proxy_set_header Sec-WebSocket-Version $http_sec_websocket_version;
                        proxy_buffering off;
                        } # end location

                # location /webmo {
                #       proxy_pass https://146.95.158.49:8443/;
                # } # end location
        } # end server
} # end http
```

Contents of `proxy.conf` (some settings overwritten by contents of `nginx.conf`)

```nginx
proxy_http_version 1.1;
proxy_set_header        Upgrade                 $http_upgrade;
proxy_set_header        Connection              "upgrade";
proxy_set_header        X-Real-IP               $remote_addr;
proxy_set_header        X-Forwarded-For         $proxy_add_x_forwarded_for;
proxy_set_header        X-Forwarded-User        $http_authorization;

#this is the maximum upload size
client_max_body_size       20m;
client_body_buffer_size    128k;

proxy_connect_timeout      90;
proxy_send_timeout         90;
proxy_read_timeout         90;
proxy_buffer_size          4k;
proxy_buffers              4 32k;
proxy_busy_buffers_size    64k;
proxy_temp_file_write_size 64k;
```

## JupyterHub TLS settings

With nginx configured on the DMZ machine, JupyterHub server will now receive traffic on port 443. To configure JupyterHub, perform the following:

- Generate a TLS key and certificate
  - `sudo openssl req -x509 -nodes -days 9999 -newkey rsa:2048 -keyout /etc/ssl/private/<key-name>.key -out /etc/ssl/certs/<cert-name>.crt`
- Enable https: `sudo tljh-config set https.enabled true`
- Set https port: `sudo tljh-config set https.port 443`
- Set key and certificate locations in TLJH
  - `sudo tljh-config set https.tls.key <key-location>`
  - `sudo tljh-config set https.tls.cert <cert-location>`

Check the following pages for info on setting up JupyterHub with a reverse proxy:

- <https://jupyterhub.readthedocs.io/en/stable/installation-guide-hard.html#setting-up-a-reverse-proxy>
- <https://jupyterhub.readthedocs.io/en/stable/reference/config-proxy.html>
- <https://github.com/jupyterhub/the-littlest-jupyterhub/issues/272>
- <https://flaviocopes.com/nginx-reverse-proxy/>

## WebMO setup

Install WebMO and TLJH according to instructions. Modify Apache and TLJH as follows:

### Set Apache to listen on 8080

Change ports.conf

- Line 5: `Listen 80` -> `Listen 8080`
- Line 8, Line 12: `Listen 443` -> `Listen 8080`

### Set Traefik to listen on 443

`sudo tljh-config set http.port 8080`
`sudo tljh-config set https.port 443`

- Set Traefik to forward traffic for http://webmo.hcpchemlab.org to http://127.0.0.1:8080
- Content of `/opt/tljh/state/rules/webmo_rules.toml`:

```toml
[frontends]
[frontends.default]
priority = 1

[frontends.jupyterhub]
backend = "jupyterhub"
passHostHeader = true
priority = 90
[frontends.jupyterhub.routes.rule1]
rule = "Host: jupyter.hcpchemlab.org"

[frontends.webmo]
backend = "webmo"
passHostHeader = true
priority = 100
[frontends.webmo.routes.rule1]
rule = "Host: webmo.hcpchemlab.org"

[backends]
[backends.jupyterhub]
[backends.jupyterhub.servers.server1]
url = "http://127.0.0.1:15001"

[backends.webmo]
[backends.webmo.servers.server1]
url = "http://127.0.0.1:8080"
```

#### Alternate option

Look into using [jupyter-server-proxy](https://jupyter-server-proxy.readthedocs.io/en/latest/), might just need to define a port and go, ignore all of the Traefik configurations.