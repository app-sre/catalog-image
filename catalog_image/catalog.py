import os
import yaml
import re

import logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


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

    def check(self, catalog_name):
        if not self.name.startswith(catalog_name):
            logging.error("Invalid .metadata.name")
            return False

        csv_name_tpl = '{}-operator.v{}.clusterserviceversion.yaml'
        expected_csv_filename = csv_name_tpl.format(catalog_name, self.version)
        if self.csv_filename != expected_csv_filename:
            logging.error(["Invalid CSV filename",
                           self.csv_filename,
                           expected_csv_filename])
            return False

        return True

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
    def __init__(self, path, channel):
        self.name = os.path.basename(path)
        self.path = path
        self.channel = channel

        self.package_filename = os.path.join(
            self.path, self.name + '.package.yaml')
        self.current_csv = self.get_current_csv()
        self.bundles = self.get_bundles()

    def package(self):
        return {
            'packageName': self.package_name,
            'channels': [
                {
                    'name': self.channel,
                    'currentCSV': self.current_csv
                }
            ]
        }

    def get_bundles(self):
        bundles = []
        try:
            for entry in os.listdir(self.path):
                full_path = os.path.join(self.path, entry)
                if os.path.isdir(full_path):
                    bundles.append(Bundle(full_path))
        except OSError:
            pass

        return bundles

    def is_bundle_valid(self, bundle):
        return bundle.check(self.name)

    def dump(self):
        with open(self.package_filename, 'w') as f:
            yaml.safe_dump(self.package(), f, default_flow_style=False)

    @property
    def package_name(self):
        return '{}-operator'.format(self.name)

    def get_current_csv(self):
        try:
            with open(self.package_filename, 'r') as f:
                content = yaml.load(f, Loader=yaml.CLoader)
                return content['channels'][0]['currentCSV']
        except IOError:
            return None

    def set_current_csv(self, csv):
        self.current_csv = csv
