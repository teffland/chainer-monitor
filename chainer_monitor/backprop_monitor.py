import chainer as ch
import numpy as np


class BackpropMonitorExtension(ch.training.extension.Extension):
    """ Trainer extension to monitor useful backward statistics of a model.

    This extension monitors variable update and gradient histograms, means,
    and standard deviations during training.

    By default, all model parameters updates and gradients are monitored.

    Intermediate variables can be monitored, but only their gradients (not updates).
    This can be useful to see when diagnosing gradient flow problems in backprop.

    Limit the monitored gradients and updates by specifying a set of `keys`.

    """
    def __init__(self,
                 target,
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
        self._init_param_history(target) # used to monitor param updates
        self.reported_grad_edges = []
        self.reported_update_edges = []

    def _init_param_history(self, target):
        """ Initialize the param history to the initial param values. """
        self.param_history = {}
        for name, link in list(target.namedlinks()):
            # get initial values of all monitored params
            if not issubclass(type(link), ch.Chain): # drill down to base links only
                for param in link.params():
                    if (self.keys is None
                        or (self.keys is not None and param.name in self.keys)):
                        if param.data is not None:
                            self.param_history['{}/{}'.format(name, param.name)] = param.data

    def _report_update_on_link(self, param, link, canon_name, name=None):
        """ Report statistics about parameter _updates_ to the link object.

        Because of chainers updater design, this can only be done by keeping
        track of the previous iterations parameter values and subracting them
        from the new parameter values.

        """
        param_name = name if name else param.name
        old_param = self.param_history[canon_name]
        update_ratio = (param.data - old_param) / (old_param+1e-15)
        if self.hist_edges is not None:
            hist, edges = np.histogram(update_ratio, bins=self.hist_edges)
            ch.reporter.report({'{}/update:hist_vals'.format(param_name):hist}, link)
            # only report bin edges the first time (cuts log size almost in half)
            if canon_name not in self.reported_update_edges:
                ch.reporter.report({'{}/update:hist_edges'.format(param_name):edges}, link)
                self.reported_update_edges.append(canon_name)

        if self.mean:
            ch.reporter.report({'{}/update:mean'.format(param_name):update_ratio.mean()}, link)
        if self.std:
            ch.reporter.report({'{}/update:std'.format(param_name):update_ratio.std()}, link)

    def _report_grad_on_link(self, param, link, canon_name, name=None):
        """ Report statistics about parameter _gradients_ to the link object.

        These can include intermediate variables in the computation,
        provided that the optimizer uses the `retain_grad=True` argument to
        `loss.backward()`.

        """
        param_name = name if name else param.name
        if param.grad is None:
            raise AttributeError("Cannot monitor gradient for variable with no `.grad` attribute.\n\
If you are monitoring an itermediate gradient, make sure the optimizer is wrapped with `RetainGrad`.")
        if self.hist_edges is not None:
            hist, edges = np.histogram(param.grad, bins=self.hist_edges)
            ch.reporter.report({'{}/grad:hist_vals'.format(param_name):hist}, link)
            # only report bin edges the first time (cuts log size almost in half)
            if canon_name not in self.reported_grad_edges:
                ch.reporter.report({'{}/grad:hist_edges'.format(param_name):edges}, link)
                self.reported_grad_edges.append(canon_name)
        if self.mean:
            ch.reporter.report({'{}/grad:mean'.format(param_name):param.grad.mean()}, link)
        if self.std:
            ch.reporter.report({'{}/grad:std'.format(param_name):param.grad.std()}, link)

    def __call__(self, trainer):
        """ Collect backward gradient and param statistics on monitored model variables. """
        # loop through all links/chains
        for name, link in list(trainer.updater._optimizers['main'].target.namedlinks()):
            # monitor all params for the base links of the models
            # TODO: clean up the use of canon name
            if not issubclass(type(link), ch.Chain): # drill down to base links only
                for param in link.params():
                    if (self.keys is None
                        or (self.keys is not None and param.name in self.keys)):
                        canon_name = '{}/{}'.format(name, param.name)

                        self._report_grad_on_link(param, link, canon_name)

                        # only report the update if we have a history
                        # we will miss the first iteration for uninitialized params
                        if canon_name in self.param_history:
                            self._report_update_on_link(param, link, canon_name)
                        self.param_history[canon_name] = param.data.copy()

            # monitor all explicitly marked variables (even if they aren't params)
            for varname, var in getattr(link, 'monitored_variables', {}).items():
                if (self.keys is None
                        or (self.keys is not None and param.name in self.keys)):
                    self._report_grad_on_link(var, link, varname, varname)
