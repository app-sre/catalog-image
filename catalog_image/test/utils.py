import os
import shutil
import subprocess
import tempfile

from contextlib import contextmanager


def get_repo_dir(name):
    return os.path.join(os.path.dirname(__file__), 'fixtures_repo_dirs', name)


@contextmanager
def clone_repo(repo_name):
    temp_dir = tempfile.mktemp()
    repo_dir = os.path.join(temp_dir, 'hive')
    shutil.copytree(get_repo_dir(repo_name), temp_dir)

    try:
        yield repo_dir
    finally:
        shutil.rmtree(repo_dir, True)


def dircmp(dir1, dir2):
    result = subprocess.Popen(['diff', '-r', dir1, dir2])
    result.communicate()
    return result.returncode == 0
