
from distutils.core import setup

setup(
    name="event-emitter-js",
    version="0.1.2",
    description="JavaScript-like EventEmitter class for Python 3",
    author="Thiago Costa",
    author_email="admin@rootbsd.info",
    url="https://github.com/thiagodk/python-event-emitter",
    package_dir={"": "src"},
    packages=["event_emitter"]
)
