from catalog_image.catalog import Catalog

from utils import clone_repo


class TestCurrentCSV(object):
    def test_current_csv_single_csv(self):
        with clone_repo('single_csv') as repo_dir:
            catalog = Catalog(repo_dir, 'staging')
            assert catalog.current_csv == 'hive-operator.v0.1.506-14cff03'

    def test_current_csv_empty(self):
        with clone_repo('empty') as repo_dir:
            catalog = Catalog(repo_dir, 'staging')
            assert catalog.current_csv is None
