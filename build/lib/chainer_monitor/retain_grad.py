from chainer import cuda
def RetainGrad(cls):
    """ Override the update function for a chainer optimizer to retain intermediate gradients.

    This is very useful for monitoring gradient flow through a network.
    """
    def update_retain_grad(self, lossfun=None, *args, **kwds):
        """Updates parameters based on a loss function or computed gradients.

        This method runs in two ways.

        - If ``lossfun`` is given, then use it as a loss function to compute
          gradients.
        - Otherwise, this method assumes that the gradients are already
          computed.

        In both cases, the computed gradients are used to update parameters.
        The actual update routines are defined by the :meth:`update_one`
        method (or its CPU/GPU versions, :meth:`update_one_cpu` and
        :meth:`update_one_gpu`).

        """
        if lossfun is not None:
            use_cleargrads = getattr(self, '_use_cleargrads', True)
            loss = lossfun(*args, **kwds)
            if use_cleargrads:
                self.target.cleargrads()
            else:
                self.target.zerograds()
            loss.backward(retain_grad=True)
            del loss

        self.reallocate_cleared_grads()

        self.call_hooks()

        self.t += 1
        for param in self.target.params():
            param.update()

        # chainer 1.x version
        # if lossfun is not None:
        #     use_cleargrads = getattr(self, '_use_cleargrads', False)
        #     loss = lossfun(*args, **kwds)
        #     if use_cleargrads:
        #         self.target.cleargrads()
        #     else:
        #         self.target.zerograds()
        #     loss.backward(retain_grad=True)
        #     del loss
        #
        # self.reallocate_cleared_grads()
        #
        # self.call_hooks()
        # self.prepare()
        #
        # self.t += 1
        # states = self._states
        # for name, param in self.target.namedparams():
        #     with cuda.get_device_from_array(param.data):
        #         self.update_one(param, states[name])

    # dynamically override the class
    return type(cls.__name__, (cls,), {'update':update_retain_grad})
