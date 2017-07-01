def monitor(name, var, obj):
    """ Monitor the forward and backward statistics of some variable.

    This function is used to mark intermediate computations in a `chainer.Link`s
    `__call__` method.

    This is necessary for `ActivationMonitorExtension` and `BackpropMonitorExtension`
    to be able to log the variables values for model training debugging.

    Args:
        `name` (str): name of variable in the `monitored_variables` dict.
        `var` (chainer.Variable): variable to monitor.
        `obj` (chainer.Link): link object to store monitored variables on.

    """
    if not hasattr(obj, 'monitored_variables'):
        obj.monitored_variables = {}
    obj.monitored_variables[name] = var
