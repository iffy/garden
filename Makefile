.PHONY: help clean tar test

help:
	@cat Makefile

#------------------------------------------------------------------------------
# remove temporary files
#------------------------------------------------------------------------------
clean:
	-find . -name "*.pyc" -exec rm {} \;
	-rm -rf _trial_temp
	-rm *.tgz
	-rm -rf MANIFEST
	-rm -rf htmlcov
	-rm .coverage.*
	-rm .coverage
	-rm -r garden.egg-info

#------------------------------------------------------------------------------
# generate a tar file for distribution
#------------------------------------------------------------------------------
tar:
	make clean
	python setup.py sdist

test:
	bash testeverything.sh