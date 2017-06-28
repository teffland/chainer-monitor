import chainer as ch

class VariableConverterUpdater(ch.training.StandardUpdater):
    """ An implementation of an updater that doesn't assume 
    the downstream model will receive a tuple or dict of chainer variables.
    
    Instead, this updater let's the converter function produce an arbitrary
    data structure of :class:`ch.Variable`s for consumption by downstream models.
        
    This is useful for sequence-based models (that don't pad), 
    where often we want to pass entire lists of 
    :class:`ch.Variable`s as individual arguments.
    """
    def __init__(self, iterator, optimizer, converter=ch.dataset.convert.concat_examples,
                 device=None, loss_func=None):
        super(VariableConverterUpdater, self).__init__(
            iterator, optimizer, converter, device, loss_func
        )
        self.n_examples = 0
        
    def update_core(self):
        batch = self._iterators['main'].next()
        self.n_examples += len(batch)
        optimizer = self._optimizers['main']
        loss_func = self.loss_func or optimizer.target
        in_vars = self.converter(batch)
        if type(in_vars) in (tuple, list):
            optimizer.update(loss_func, *in_vars)
        elif isinstance(in_vars, dict):
            optimizer.update(loss_func, **in_vars)
        else:
            optimizer.update(loss_func, in_vars)