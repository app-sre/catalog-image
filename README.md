![](https://img.shields.io/github/license/app-sre/qontract-reconcile.svg?style=flat)

# catalog-image

Command to organize [OLM](https://github.com/operator-framework/operator-lifecycle-manager) bundles into a [catalog registry](https://github.com/operator-framework/operator-registry), and stores the state in a Git repo.

This is an opinionated tool:

- Given a component named `<component>`, the CSV will be `<component>-operator.v<version>`.
- Each component has a single channel.

## Configuration

This tool is config file driven. All the commands require a `--config config.yaml` option.

Example `config.yaml`:

```yaml
git-url: "https://github.com/app-sre/saas-hive-operator-bundle/"
git-branch: "staging"
git-user: "optional"
git-token: "<token>"
git-name: "App-SRE"
git-email: "sd-app-sre@redhat.com"
component: "hive"
channel: "staging"
```

In order to push, this tool will embed the `git-user` and `git-token` parameters in the `git-url`. Example: `https://optional:<token>@github.com/app-sre/saas-hive-operator-bundle/`.

The `git-name` and `git-email` fields will be used for the `git-author` field.

## Installation

Create and enter the [virtualenv](https://virtualenv.pypa.io/en/latest/) environment:

```sh
virtualenv venv
source venv/bin/activate

# make sure you are running the latest setuptools
pip install --upgrade pip setuptools
```

Install the package:

```sh
python setup.py install
```

## Usage

### `current-csv`

Prints the latest csv from the package file.

```
Usage: catalog-image current-csv [OPTIONS]

Options:
  --remove-temp-dir / --no-remove-temp-dir
  --help                          Show this message and exit.
```

### `add-bundle`

Adds a new bundle in `BUNDLE_PATH` to the catalog and sets the correct `currentCSV` in the package file.

```
Usage: catalog-image add-bundle [OPTIONS] BUNDLE_PATH

Options:
  --remove-temp-dir / --no-remove-temp-dir
  --push / --no-push
  --prune-after TEXT
  --help                          Show this message and exit.
```

## Docker

This tool can be used with Docker.

Example:

```sh
docker run --rm -v ${PWD}/config.yaml:/config.yaml \
    quay.io/app-sre/catalog-image:latest \
    catalog-image --config /config.yaml current-csv
```

## Limitations

- `git-url` must be `https` based. `ssh` is not currently supported.

## Licence

[Apache License Version 2.0](LICENSE).

## Authors

These tools have been written by the [Red Hat App-SRE Team](sd-app-sre@redhat.com).
