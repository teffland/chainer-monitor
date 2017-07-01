import json
import os
import shutil
import tempfile
import six
import numpy as np

from chainer.training.extensions import LogReport
from array_summary import DictArraySummary

class BetterLogReport(LogReport):
    """ Subclass LogReport to handle numpy arrays reporting """
    def __call__(self, trainer):
        # accumulate the observations
        keys = self._keys
        observation = trainer.observation
        summary = self._summary

        if keys is None:
            summary.add(observation)
        else:
            summary.add({k: observation[k] for k in keys if k in observation})

        if self._trigger(trainer):
            # output the result
            stats = self._summary.compute_mean()
            stats_cpu = {}
            for name, value in six.iteritems(stats):
                if isinstance(value, np.ndarray):
                    value[np.isnan(value)] = 0.
                    stats_cpu[name] = value.tolist()
                else:
                    if np.isnan(value): value = 0.
                    stats_cpu[name] = float(value)  # copy to CPU

            updater = trainer.updater
            stats_cpu['epoch'] = updater.epoch
            stats_cpu['iteration'] = updater.iteration
            # get total number of examples seen so far
            main_iter = updater._iterators['main']
            stats_cpu['n_examples'] = len(main_iter.dataset)*main_iter.epoch_detail
            stats_cpu['elapsed_time'] = trainer.elapsed_time

            if self._postprocess is not None:
                self._postprocess(stats_cpu)

            self._log.append(stats_cpu)

            # write to the log file
            if self._log_name is not None:
                log_name = self._log_name.format(**stats_cpu)
                fd, path = tempfile.mkstemp(prefix=log_name, dir=trainer.out)
                with os.fdopen(fd, 'w') as f:
                    json.dump(self._log, f, indent=4)

                new_path = os.path.join(trainer.out, log_name)
                shutil.move(path, new_path)

            # reset the summary for the next output
            self._init_summary()

    def _init_summary(self):
        self._summary = DictArraySummary()
