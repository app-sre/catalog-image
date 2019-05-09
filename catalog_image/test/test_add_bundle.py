from catalog_image.catalog import Catalog, Bundle
from utils import clone_repo, fixture_bundle, fixture_repo_dir, dircmp


class TestAddBundle(object):
    def test_add_bundle_from_empty(self):
        with clone_repo() as repo_dir:
            source_bundle_dir = fixture_bundle('0.1.506-14cff03')
            catalog = Catalog(repo_dir, 'staging')

            source_bundle = Bundle(source_bundle_dir)
            bundle = catalog.add_bundle(source_bundle)

            assert source_bundle.name == 'hive-operator.v0.1.506-14cff03'
            assert bundle.name == source_bundle.name

            assert dircmp(fixture_repo_dir('single_csv/hive'), repo_dir)
