import numpy as np
import chainer as ch

class ActivationMonitorExtension(ch.training.extension.Extension):
    """ Trainer extension to monitor useful forward statistics of a model.

    This extension monitors variable histograms, means,
    and standard deviations during training.

    By default, all model parameters are monitored.
    Additional intermediate computations can be monitored using the `monitor`
    helper function in the `__call__` definition of a model.

    Limit the monitored activations by specifying a set of `keys`.

    """
    def __init__(self,
                 keys=None,
                 hist_edges=[-1e15, -1e5, -1e4, -1e3, -1e2, -1e1, -1e-1, -1e-2, -1e-3, -1e-4,
                                 0., 1e-4, 1e-3, 1e-2, 1e-1, 1e1, 1e2, 1e3, 1e4, 1e5, 1e15],
                 mean=True,
                 std=True):
        self.priority = 'PRIORITY_WRITER'
        self.keys = keys
        self.hist_edges = np.array(hist_edges)
        self.mean = mean
        self.std = std
        self.reported_edges = []

    def _report_param_on_link(self, param, link, name=None):
        """ Report observations to link object. """
        param_name = name if name else param.name
        canon_name = '{}/{}'.format(link.name, param_name)
        if self.hist_edges is not None:
            hist, edges = np.histogram(param.data, bins=self.hist_edges)
            ch.reporter.report({'{}/data:hist_vals'.format(param_name):hist}, link)
            # only report bin edges the first time (cuts log size almost in half)
            if canon_name not in self.reported_edges:
                ch.reporter.report({'{}/data:hist_edges'.format(param_name):edges}, link)
                self.reported_edges.append(canon_name)
        if self.mean:
            ch.reporter.report({'{}/data:mean'.format(param_name):param.data.mean()}, link)
        if self.std:
            ch.reporter.report({'{}/data:std'.format(param_name):param.data.std()}, link)


    def __call__(self, trainer):
        """ Collect forward activation statistics on monitored variables. """
        # loop through all links/chains
        for name, link in list(trainer.updater._optimizers['main'].target.namedlinks()):
            # monitor all params for the base links of the models
            if not issubclass(type(link), ch.Chain): # drill down to base links only
                for param in link.params():
                    if (self.keys is None
                        or (self.keys is not None and param.name in self.keys)):
                        self._report_param_on_link(param, link)

            # monitor all explicitly marked variables (even if they aren't params)
            for varname, var in getattr(link, 'monitored_variables', {}).items():
                if (self.keys is None
                        or (self.keys is not None and param.name in self.keys)):
                    self._report_param_on_link(var, link, varname)
