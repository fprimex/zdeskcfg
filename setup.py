from setuptools import setup
import sys

should_2to3 = sys.version >= '3'

setup(name="zdeskcfg",
      version="1.0.0",
      description="Easy configuration of zendesk/zdesk scripts.",
      long_description="Easy configuration of zendesk/zdesk scripts.",
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
