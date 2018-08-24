from setuptools import setup
import sys

with open("README.txt") as readme_file:
      long_description = readme_file.read()

setup(name="zdeskcfg",
      version="1.1.0",
      description="Easy configuration of zendesk/zdesk scripts.",
      long_description=long_description,
      py_modules=["zdeskcfg"],
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries",
      ],
      keywords="zendesk zdesk config",
      author="Brent Woodruff",
      author_email="brent@fprimex.com",
      url="http://github.com/fprimex/zdeskcfg",
      license="BSD",
      zip_safe=False,
      install_requires=["plac_ini"]
)
