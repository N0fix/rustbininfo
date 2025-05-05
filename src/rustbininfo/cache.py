import pathlib

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from xdg_base_dirs import xdg_cache_home

package_name = __package__ if __package__ is not None else "RBI"

cache_dir = pathlib.Path(xdg_cache_home()) / package_name
cache_lock_dir = cache_dir / "lock"
cache_dir.mkdir(exist_ok=True, parents=True)
cache_lock_dir.mkdir(exist_ok=True, parents=True)

cache_opts = {"cache.type": "file", "cache.data_dir": cache_dir, "cache.lock_dir": cache_lock_dir}
cache: CacheManager = CacheManager(**parse_cache_config_options(cache_opts))
tmpl_cache = cache.get_cache("mytemplate.html", type="dbm")
