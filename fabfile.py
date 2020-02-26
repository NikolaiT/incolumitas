from fabric.api import *
import fabric.contrib.project as project
import os
import shutil
import sys
import SocketServer

from pelican.server import ComplexHTTPRequestHandler

# Local path configuration (can be absolute or relative to fabfile)
env.deploy_path = 'output'
DEPLOY_PATH = env.deploy_path

# Remote server configuration
production = 'nikolai@incolumitas.com'
dest_path = '/var/www/incolumitas.com/'

# Rackspace Cloud Files configuration settings
env.cloudfiles_username = 'my_rackspace_username'
env.cloudfiles_api_key = 'my_rackspace_api_key'
env.cloudfiles_container = 'my_cloudfiles_container'

# Github Pages configuration
env.github_pages_branch = "gh-pages"

# Port for `serve`
PORT = 8000

def clean():
    """Remove generated files"""
    if os.path.isdir(DEPLOY_PATH):
        shutil.rmtree(DEPLOY_PATH)
        os.makedirs(DEPLOY_PATH)

def build():
    """Build local version of site"""
    local('pelican -s pelicanconf.py')

def rebuild():
    """`clean` then `build`"""
    clean()
    build()

def regenerate():
    """Automatically regenerate site upon file modification"""
    local('pelican -r -s pelicanconf.py')

def serve():
    """Serve site at http://localhost:8000/"""
    os.chdir(env.deploy_path)

    class AddressReuseTCPServer(SocketServer.TCPServer):
        allow_reuse_address = True

    server = AddressReuseTCPServer(('', PORT), ComplexHTTPRequestHandler)

    sys.stderr.write('Serving on port {0} ...\n'.format(PORT))
    server.serve_forever()

def reserve():
    """`build`, then `serve`"""
    build()
    serve()

def preview():
    """Build production version of site"""
    local('pelican -s publishconf.py')

def cf_upload():
    """Publish to Rackspace Cloud Files"""
    rebuild()
    with lcd(DEPLOY_PATH):
        local('swift -v -A https://auth.api.rackspacecloud.com/v1.0 '
              '-U {cloudfiles_username} '
              '-K {cloudfiles_api_key} '
              'upload -c {cloudfiles_container} .'.format(**env))

@hosts(production)
def publish():
    """Publish to production via rsync"""
    local('pelican -s publishconf.py')
    project.rsync_project(
        remote_dir=dest_path,
        exclude=".DS_Store",
        local_dir=DEPLOY_PATH.rstrip('/') + '/',
        delete=True,
        extra_opts='-c',
    )

@hosts(production)
def isso():
    """Publish to production via rsync"""

    # local('scp -i /home/nikolai/.ssh/root_new_server /home/nikolai/projects/work/backups/var/lib/isso/comments.db root@167.99.241.135:/var/lib/isso/comments.db')

    local('scp -i /home/nikolai/.ssh/root_new_server /home/nikolai/projects/private/incolumitas/incolumitas/isso/isso.cfg root@167.99.241.135:/etc/isso.cfg')

    local('scp -i /home/nikolai/.ssh/root_new_server /home/nikolai/projects/private/incolumitas/incolumitas/isso/isso_nginx.conf root@167.99.241.135:/etc/nginx/sites-available/isso_nginx.conf')

    # local('ssh -i /home/nikolai/.ssh/root_new_server root@167.99.241.135 "ln -s /etc/nginx/sites-available/isso_nginx.conf /etc/nginx/sites-enabled/isso_nginx.conf"')

    local('scp -i /home/nikolai/.ssh/root_new_server /home/nikolai/projects/private/incolumitas/incolumitas/isso/isso.service root@167.99.241.135:/etc/systemd/system/isso.service')

    local('ssh -i /home/nikolai/.ssh/root_new_server root@167.99.241.135 "systemctl daemon-reload && systemctl restart isso && systemctl restart nginx"')

@hosts(production)
def publish2():
    """Publish to production via rsync"""
    local('pelican -s publishconf.py')
    local("""rsync -avc --delete -e "ssh -i /home/nikolai/.ssh/root_new_server" output/ root@167.99.241.135:/var/www/incolumitas.com/""")
    local('ssh -i /home/nikolai/.ssh/root_new_server root@167.99.241.135 "chown -R www-data:www-data /var/www/incolumitas.com/"')

def gh_pages():
    """Publish to GitHub Pages"""
    rebuild()
    local("ghp-import -b {github_pages_branch} {deploy_path}".format(**env))
    local("git push origin {github_pages_branch}".format(**env))
