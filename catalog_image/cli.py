import os
import shutil
import sys
import tempfile
import urlparse

from contextlib import contextmanager

import click
import git
import yaml

from catalog import Catalog, Bundle


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


def add_auth_to_url(url, user, password):
    url_split = list(urlparse.urlsplit(url))

    if '@' in url_split[1]:
        click.echo("URL already has auth", err=True)
        sys.exit(1)

    url_split[1] = '{}:{}@{}'.format(user, password, url_split[1])
    return urlparse.urlunsplit(url_split)


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


@click.group()
@click.option("--config", type=click.Path())
@click.pass_context
def run(ctx, config, **kwargs):
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config(config, ctx.params)


@run.command()
@click.option('--remove-temp-dir/--no-remove-temp-dir', default=True)
@click.pass_context
def current_csv(ctx, remove_temp_dir):
    config = ctx.obj['config']

    with clone_repo(config, remove_temp_dir) as repo_dir:
        path = os.path.join(repo_dir, config['component'])
        channel = config['channel']

        catalog = Catalog(path, channel)
        click.echo(catalog.current_csv)


@run.command()
@click.option('--remove-temp-dir/--no-remove-temp-dir', default=True)
@click.option('--push/--no-push', default=True)
@click.option('--prune-after')
@click.argument('bundle_path', type=click.Path(exists=True, file_okay=False))
@click.pass_context
def add_bundle(ctx, remove_temp_dir, push, prune_after, bundle_path):
    config = ctx.obj['config']
    author = git.Actor(config['git-name'], config['git-email'])
    channel = config['channel']

    source_bundle = Bundle(bundle_path)

    with clone_repo(config, remove_temp_dir) as repo_dir:
        path = os.path.join(repo_dir, config['component'])

        catalog = Catalog(path, channel)

        if catalog.bundle_exists(source_bundle):
            click.echo("Bundle already exists", err=True)
            sys.exit(1)

        if not catalog.is_bundle_valid(source_bundle):
            click.echo("Invalid bundle", err=True)
            sys.exit(1)

        if prune_after:
            catalog.prune_after(prune_after)

        bundle = catalog.add_bundle(source_bundle)

        repo = git.Repo(repo_dir)
        repo.git.add(A=True)

        if len(repo.index.diff("HEAD")) == 0:
            click.echo("No changes detected", err=True)
            sys.exit(1)

        repo.index.commit("Adds {}".format(bundle.name), author=author)

        if push:
            origin = repo.remote(name='origin')
            origin.push()
