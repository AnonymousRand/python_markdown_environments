import pytest

from markdown_environments.thms import *


def test_init_extension_with_configs_error():
    with pytest.raises(KeyError) as e:
        _ = ThmsExtension(nonexistent_config="")
        assert "'nonexistent_config' (did you pass in an invalid config key to ThmsExtension.__init__()?)" in e
