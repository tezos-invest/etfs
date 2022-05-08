import pathlib

import pytest


@pytest.fixture(scope='session')
def resources():
    return pathlib.Path(__file__).parent.parent / 'resources'
