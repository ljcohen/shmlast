#!/usr/bin/env python
from os.path import join, dirname
rel_path = dirname(__file__)
__version__ = open(join(rel_path, 'VERSION')).read().strip()


from . import crbl
from . import util
from . import hits
from . import last
from . import transeq

