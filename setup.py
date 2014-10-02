from setuptools import setup
import sys

should_2to3 = sys.version >= '3'

with open("README.txt") as readme_file:
      long_description = readme_file.read()

setup(name="zdeskcfg",
      version="1.0.3",
      description="Easy configuration of zendesk/zdesk scripts.",
      long_description=long_description,
      py_modules=["zdeskcfg"],
      classifiers=["Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries",
      ],
      use_2to3=should_2to3,
      keywords="zendesk zdesk config",
      author="Brent Woodruff",
      author_email="brent@fprimex.com",
      url="http://github.com/fprimex/zdeskcfg",
      license="BSD",
      zip_safe=False,
      install_requires=["plac_ini"]
)
