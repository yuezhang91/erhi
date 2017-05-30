# This file is part of erhi project.
# https://github.com/FredSUEE/erhi

# install all dependencies (do not forget to create a virtualenv first)
install:
	@pip install -U .

# install the package in development mode, including all dependencies
# (do not forget to create a virtualenv first)
setup:
	@pip install -U -e .\[tests\]
