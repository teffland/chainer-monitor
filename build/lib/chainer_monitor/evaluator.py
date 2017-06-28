import copy
import chainer as ch

class VariableConverterEvaluator(ch.training.extensions.Evaluator):
    """ An implementation of an evaluator that doesn't assume
    the downstream model will receive a tuple or dict of chainer variables.

    Instead, this evaluator let's the converter function produce an arbitrary
    data structure of :class:`ch.Variable`s for consumption by downstream models.

    It is the sibling implementation of :class:`VariableConverterUpdater`.

    The `converter` function must take the keyword argument `volatile`.

    This is useful for sequence-based models, where often we want to pass
    entire lists of :class:`ch.Variable`s as arguments.
    """
    def evaluate(self):
        """Evaluates the model and returns a result dictionary.

        This method runs the evaluation loop over the validation dataset. It
        accumulates the reported values to :class:`~chainer.DictSummary` and
        returns a dictionary whose values are means computed by the summary.

        Users can override this method to customize the evaluation routine.

        Returns:
            dict: Result dictionary. This dictionary is further reported via
                :func:`~chainer.report` without specifying any observer.

        """
        iterator = self._iterators['main']
        target = self._targets['main']
        eval_func = self.eval_func or target

        if self.eval_hook:
            self.eval_hook(self)
        it = copy.copy(iterator)
        summary = ch.reporter.DictSummary()

        for batch in it:
            observation = {}
            with ch.reporter.report_scope(observation):
                with ch.no_backprop_mode():
                    in_vars = self.converter(batch)
                    if type(in_vars) in (tuple, list):
                        eval_func(*in_vars)
                    elif isinstance(in_vars, dict):
                        eval_func(**in_vars)
                    else:
                        eval_func(in_vars)
            summary.add(observation)

        return summary.compute_mean()
