from distutils.core import setup
from setuptools import find_packages

try:
    from caral.version import __version__
except ModuleNotFoundError:
    exec(open("caral/version.py").read())

setup(name="python-rts",
      version=__version__,
      packages=find_packages(),
      package_data={p: ['*'] for p in find_packages()},
      description="Package for in-car BUS analysis",
      url="https://github.com/j-schmied",
      author="Jannik Schmied",
      author_email="jannik.schmied@pm.me",
      license="MIT",
      install_requires=[
          "keyboard",
          "matplotlib",
          "numpy",
          "pandas",
          "psutil",
          "python_ics",
          "seaborn",
          "scapy",
      ],
      zip_safe=False
      )
