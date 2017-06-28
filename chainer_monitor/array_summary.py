import chainer as ch
from chainer.reporter import _get_device
import numpy as np
import collections
import six

class ArraySummary(ch.reporter.Summary):
    """ Summary class that can additionally handle numpy arrays, not just scalars. 
    
    This allows for online summarization of arrays, elementwise."""
    def __init__(self):
        self._x = None
        self._x2 = None
        self._n = 0
        self._shape = None
        
    def add(self, value):
        """Adds an array value.

        Args:
            value: np.array value to accumulate. It is a scalar or a numpy array (on CPU or GPU).

        """
        with _get_device(value):
            if self._x is None:
                self._x = value
                self._x2 = value * value
                self._n = 1
                if np.isscalar(value):
                    self._shape = 'scalar'
                else:
                    self._shape = value.shape     
            else:
                if self._shape == 'scalar':
                    assert np.isscalar(value), "Summary value shape must not consistent."
                else:
                    assert value.shape == self._shape, "Summary value shape must not consistent."
                self._x += value
                self._x2 += value * value
                self._n += 1
                
class DictArraySummary(ch.reporter.DictSummary):
    def __init__(self):
        self._summaries = collections.defaultdict(ArraySummary)

    def add(self, d):
        """Adds a dictionary of scalars or numpy arrays.

        Args:
            d (dict): Dictionary of scalars or numpy arrays to accumulate.

        """
        summaries = self._summaries
        for k, v in six.iteritems(d):
            if isinstance(v, ch.Variable):
                v = v.data
            if np.isscalar(v) or isinstance(v, np.ndarray):
                summaries[k].add(v)