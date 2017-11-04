import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

master_doc = 'index'
source_suffix = '.txt'
exclude_patterns = ['_build']
extensions = ['sphinxcontrib.reviewbuilder']
numfig = True
