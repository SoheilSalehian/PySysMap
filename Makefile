# Author: David Said (david.said@gmail..com)
# Modified: Soheil Salehian (soheil.salehian@gmail.com)
# Makefile for the PySys project

# Gedit autosave files are deleted by the clean rule
geditAutosaves = $(shell find . -type f -name '*~')
# Python compiled files are deleted by the clean rule
compiledPyFiles =  $(shell find . -type f -name '*.pyc')
# Python modules are tracked by the documentation rule
pythonModules = $(shell find . -type f -name '*.py')

#perlModules = $(shell find . -type f -name '*.pm')  $(shell find . -type f -name '*.pl')  $(shell find . -type f -name '*.tc') $(shell find . -type f -name '*.tt')
## .ui files are tracked by the ui compilation rule
#uifiles  = $(shell find . -type f -name '*.ui')
## Pyqt ui files are deleted by the clean rule
#pyuifiles = $(uifiles:.ui=.py)
# The index file is considered to be the output of the documentation rule
doc = doc/html/index.html
# The all-inclusive rule provokes the documentation and ui rules to be checked.
#all: doc ui
all: doc 
# The documentation rule has the index file as a dependency
doc: $(doc)
# The index file has all the python modules as a dependency, so every time they change, this rul may be triggered
$(doc): pythonDoc

# The rule to make the python documentation
pythonDoc: $(pythonModules)
	doxygen doxyfile-python

## The ui rule has the .ui files as dependencies
#ui: $(pyuifiles)
## This rule compiles the ui files to generate theur corresponding .py file
#$(pyuifiles): %.py: %.ui
#	pyuic4 $< -o $@

# The clean rule deletes all non-source files, to make clean commits    
clean:
#	rm -rf doc/python
	rm -rf $(geditAutosaves)
#	rm -rf $(pyuifiles)
	rm -rf $(compiledPyFiles)

