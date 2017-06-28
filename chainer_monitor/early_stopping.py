from chainer import reporter
from chainer.training import util
import pprint

class PatientBestValueTrigger(object):
    """Trigger invoked some patient interval after a specific value becomes best.

    This trigger basically implements early stopping for a trainer.

    Args:
        key (str): Key of value.
        patience (int): number of trigger evaluations to wait until responding true
        compare (function): Compare function which takes current best value and
            new value and returns whether new value is better than current
            best.
        trigger: Trigger that decides the comparison interval between current
            best value and new value. This must be a tuple in the form of
            ``<int>, 'epoch'`` or ``<int>, 'iteration'`` which is passed to
            :class:`~chainer.training.triggers.IntervalTrigger`.
        max_trigger: IntervalTrigger that will return true after some predecided amount.

    """
    def __init__(self, key, patience, compare, trigger=(1, 'epoch'), max_trigger=(1000, 'epoch')):
        self._key = key
        self._patience = patience
        self._waited = 0
        self._best_value = None
        self._interval_trigger = util.get_trigger(trigger)
        self._max_trigger = util.get_trigger(max_trigger)
        self._init_summary()
        self._compare = compare

    def __call__(self, trainer):
        """Decides whether the extension should be called on this iteration.

        Args:
            trainer (~chainer.training.Trainer): Trainer object that this
                trigger is associated with. The ``observation`` of this trainer
                is used to determine if the trigger should fire.

        Returns:
            bool: ``True`` if the corresponding extension should be invoked in
                this iteration.

        """
        observation = trainer.observation
        summary = self._summary
        key = self._key
        if key in observation:
            summary.add({key: observation[key]})

        if not self._interval_trigger(trainer):
            return False

        if self._max_trigger(trainer):
            return True

        stats = summary.compute_mean()
        value = float(stats[key])  # copy to CPU
        self._init_summary()

        if not self._best_value or self._compare(self._best_value, value):
            self._best_value = value
            self._waited = 0
            return False
        elif self._waited >= self._patience:
            return True
        else:
            self._waited += 1
            if self._waited >= self._patience:
                return True
            else:
                return False

    def _init_summary(self):
        self._summary = reporter.DictSummary()


class PatientMaxValueTrigger(PatientBestValueTrigger):
    """Trigger invoked some interval after specific value becomes maximum.

    This trigger basically implements early stopping

    Args:
        key (str): Key of value. The trigger fires when the value associated
            with this key becomes maximum.
        patience (int): Number of trigger evaluations to wait
        trigger: Trigger that decides the comparison interval between current
            best value and new value. This must be a tuple in the form of
            ``<int>, 'epoch'`` or ``<int>, 'iteration'`` which is passed to
            :class:`~chainer.training.triggers.IntervalTrigger`.
        max_trigger: IntervalTrigger that fires if we've reached the max number of iterations

    """

    def __init__(self, key, patience, trigger=(1, 'epoch'), max_trigger=(1000, 'epoch')):
        super(PatientMaxValueTrigger, self).__init__(
            key, patience,
            lambda max_value, new_value: new_value >= max_value,
            trigger, max_trigger)



class PatientMinValueTrigger(PatientBestValueTrigger):
    """Trigger invoked some interval after specific value becomes minimum.

    This trigger basically implements early stopping

    Args:
        key (str): Key of value. The trigger fires when the value associated
            with this key becomes maximum.
        patience (int): Number of trigger evaluations to wait
        trigger: Trigger that decides the comparison interval between current
            best value and new value. This must be a tuple in the form of
            ``<int>, 'epoch'`` or ``<int>, 'iteration'`` which is passed to
            :class:`~chainer.training.triggers.IntervalTrigger`.
        max_trigger: IntervalTrigger that fires if we've reached the max number of iterations

    """
    def __init__(self, key, patience, trigger=(1, 'epoch'), max_trigger=(1000, 'epoch')):
        super(PatientMinValueTrigger, self).__init__(
            key, patience,
            lambda min_value, new_value: new_value <= min_value,
            trigger, max_trigger)
