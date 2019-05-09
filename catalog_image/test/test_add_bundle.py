import pytest

from catalog_image.catalog import Catalog, Bundle, PruneCSVNotFoundError
from utils import clone_repo, fixture_bundle, fixture_repo_dir, dircmp


class TestAddBundle(object):
    def test_add_bundle_from_empty(self):
        with clone_repo() as repo_dir:
            source_bundle_dir = fixture_bundle('0.1.506-14cff03')
            catalog = Catalog(repo_dir, 'staging')

            source_bundle = Bundle(source_bundle_dir)
            bundle = catalog.add_bundle(source_bundle)

            assert catalog.current_csv == source_bundle.name
            assert bundle.name == source_bundle.name

            assert dircmp(fixture_repo_dir('single_csv/hive'), repo_dir)

    def test_add_bundle_replaces(self):
        for d in ['wo', 'null', 'invalid']:
            with clone_repo('single_csv') as repo_dir:
                bd = 'replaces/{}/0.1.513-e8c06c0'.format(d)
                source_bundle_dir = fixture_bundle(bd)
                catalog = Catalog(repo_dir, 'staging')
                prev_csv = catalog.current_csv

                source_bundle = Bundle(source_bundle_dir)
                bundle = catalog.add_bundle(source_bundle)

                assert catalog.current_csv == source_bundle.name
                assert bundle.name == source_bundle.name

                assert bundle.replaces == prev_csv
                assert prev_csv != catalog.current_csv
                assert catalog.current_csv == 'hive-operator.v0.1.513-e8c06c0'

                assert dircmp(fixture_repo_dir('replaces/hive'), repo_dir)


class TestPrune(object):
    def test_prune(self):
        with clone_repo('many_csvs') as repo_dir:
            catalog = Catalog(repo_dir, 'staging')
            prev_csv = catalog.current_csv
            bundles_prev = catalog.bundles

            prune_after = "hive-operator.v0.1.598-1af4d6f"
            catalog.prune_after(prune_after)

            assert catalog.current_csv != prev_csv
            assert catalog.current_csv == prune_after

            assert len(bundles_prev) > len(catalog.bundles)

            assert dircmp(fixture_repo_dir('prune/hive'), repo_dir)

    def test_add_bundle_prune(self):
        with clone_repo('many_csvs') as repo_dir:
            catalog = Catalog(repo_dir, 'staging')

            prune_after = "hive-operator.v0.1.598-1af4d6f"
            catalog.prune_after(prune_after)

            source_bundle_dir = fixture_bundle('0.1.700-0000000')

            source_bundle = Bundle(source_bundle_dir)
            catalog.add_bundle(source_bundle)

            assert catalog.current_csv == 'hive-operator.v0.1.700-0000000'

            assert dircmp(fixture_repo_dir('prune_plus_bundle/hive'), repo_dir)

    def test_prune_invalid(self):
        with clone_repo('many_csvs') as repo_dir:
            catalog = Catalog(repo_dir, 'staging')

            with pytest.raises(PruneCSVNotFoundError):
                catalog.prune_after("invalid")
