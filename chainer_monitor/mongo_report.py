import json
import os
import shutil
import tempfile
import six
import numpy as np
from pymongo import MongoClient

from better_report import BetterLogReport

import logging
logging.basicConfig(level=logging.INFO,
    format='[%(levelname)s] %(asctime)s: %(name)s: %(message)s')
logger = logging.getLogger(__name__)

class MongoLogReport(BetterLogReport):
    """ Subclass BetterLogReport to write log to mongo db """
    def __init__(self, uid, mongo_config, **super_kwds):
        super(MongoLogReport, self).__init__(**super_kwds)
        self.uid = uid
        client = MongoClient('mongodb://{username}:{password}@{host}:{port}/{database}'.format(
            **mongo_config))
        self.db = client[mongo_config['database']]['log']
        self._backlog = []


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
            stats_cpu['n_examples'] = getattr(updater, 'n_examples', 0) # only works with `VariableConverterUpdater`
            stats_cpu['elapsed_time'] = trainer.elapsed_time
            stats_cpu['uid'] = self.uid

            if self._postprocess is not None:
                self._postprocess(stats_cpu)

            # write to the log db
            # sometimes an insert times out.
            # if that happens than we add the instance to the backlog
            # and try to insert next time around
            if len(self._backlog):
                try:
                    self.db.insert_many(self._backlog)
                    self._backlog = []
                except:
                    logger.warning('Could not insert backlog')
            try:
                self.db.insert_one(stats_cpu)
            except:
                logging.warning('Could not insert log entry. Adding to backlog.')
                self._backlog.append(stats_cpu)

            # reset the summary for the next output
            self._init_summary()
