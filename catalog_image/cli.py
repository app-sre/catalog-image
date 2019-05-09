import os
import sys

import click
import git

from utils import clone_repo, load_config
from catalog import Catalog, PruneCSVNotFoundError, Bundle


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
            try:
                catalog.prune_after(prune_after)
            except PruneCSVNotFoundError:
                click.echo("Prune CSV not found", err=True)
                sys.exit(1)

        bundle = catalog.add_bundle(source_bundle)

        repo = git.Repo(repo_dir)
        repo.git.add(A=True)

        if len(repo.index.diff("HEAD")) == 0:
            click.echo("No changes detected", err=True)
            sys.exit(1)

        repo.index.commit("Adds {}".format(bundle.name),
                          committer=author, author=author)

        if push:
            origin = repo.remote(name='origin')
            origin.push()
