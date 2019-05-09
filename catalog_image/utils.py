import os
import shutil
import sys
import urlparse
from contextlib import contextmanager

import click
import git
import tempfile
import yaml


def check_config_file(config):
    required_keys = [
        'git-url',
        'git-branch',
        'component',
        'git-token',
        'git-name',
        'git-email',
        'channel'
    ]

    error = False
    for key in required_keys:
        if key not in config:
            click.echo('Error: Required key: {}'.format(key))
            error = True

    if error:
        sys.exit(1)


def load_config(config_file, params):
    with open(config_file, 'r') as f:
        config = yaml.load(f, Loader=yaml.CLoader)

    for key, value in params.items():
        if value is not None:
            key = key.replace("_", "-")
            config[key] = value

    check_config_file(config)

    return config


def add_auth_to_url(url, user, password):
    url_split = list(urlparse.urlsplit(url))

    if '@' in url_split[1]:
        click.echo("URL already has auth", err=True)
        sys.exit(1)

    url_split[1] = '{}:{}@{}'.format(user, password, url_split[1])
    return urlparse.urlunsplit(url_split)


@contextmanager
def clone_repo(config, remove_temp_dir):
    repo_dir = tempfile.mktemp(dir=os.environ.get('TEMP_DIR'))
    url = add_auth_to_url(config['git-url'], config.get('git-user', 'none'),
                          config['git-token'])
    git.Repo.clone_from(url, repo_dir, depth=1,
                        branch=config['git-branch'])
    try:
        yield repo_dir
    finally:
        if remove_temp_dir:
            shutil.rmtree(repo_dir)
        else:
            click.echo(["repo_dir", repo_dir])
