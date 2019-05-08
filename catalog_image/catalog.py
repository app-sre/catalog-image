import os
import yaml


class Bundle(object):
    csv = None
    csv_filename = None

    def __init__(self, path):
        self.path = path
        self.load()

    def load(self):
        for entry in os.listdir(self.path):
            full_path = os.path.join(self.path, entry)

            if entry.endswith(".clusterserviceversion.yaml"):
                self.csv_filename = entry
                with open(full_path, 'r') as f:
                    self.csv = yaml.load(f, Loader=yaml.CLoader)

    def dump(self):
        csv_path = os.path.join(self.path, self.csv_filename)

        with open(csv_path, 'w') as f:
            yaml.safe_dump(self.csv, f, default_flow_style=False)

    @property
    def name(self):
        return self.csv['metadata']['name']

    @property
    def version(self):
        return self.csv['spec']['version']

    @property
    def replaces(self):
        return self.csv['spec'].get('replaces')

    @replaces.setter
    def replaces(self, val):
        self.csv['spec']['replaces'] = val


class Catalog(object):
    name = None
    package = None
    package_filename = None
    bundles = []

    def __init__(self, path):
        self.name = os.path.basename(path)
        self.path = path
        self.load()

    def load(self):
        for entry in os.listdir(self.path):
            full_path = os.path.join(self.path, entry)

            if entry.endswith(".package.yaml"):
                self.package_filename = entry
                with open(full_path, 'r') as f:
                    self.package = yaml.load(f, Loader=yaml.CLoader)
            elif os.path.isdir(full_path):
                self.bundles.append(Bundle(full_path))

    def dump(self):
        package_filename = os.path.join(self.path, self.package_filename)

        with open(package_filename, 'w') as f:
            yaml.safe_dump(self.package, f, default_flow_style=False)

    def is_bundle_valid(self, bundle):
        return bundle.name.startswith(self.package['packageName'])

    @property
    def package_name(self):
        return self.package['packageName']

    def current_csv(self, channel):
        for c in self.package['channels']:
            if c['name'] == channel:
                return c['currentCSV']

    def set_current_csv(self, channel, csv):
        for c in self.package['channels']:
            if c['name'] == channel:
                c['currentCSV'] = csv
