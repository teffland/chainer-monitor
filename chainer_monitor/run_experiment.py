""" Start training a new Chainer model from a config file.

TODO:
* [X] create experiment dir and subdirs
* [X] git commit with autoadd and add commit hash to config
* [X] output filled in config file into experiment dir
* [X] implement early stopping with patience extension
* [X] log examples per second, iterations per second, epochs per second, estimated time left
* [X] email on error or completion
* [X] description of experiment in yaml file
* [ ] be able to restart an experiment from an existing experiment dir
* [ ] config file can optionally provide dictionary of prereq models, that will be loaded apriori and passed into this experiment to allow for forking experiments that depend on previous models (but aren't just a continuation of the same experiment.
* [ ] refactor to make more flexible
    (eg mongo password and config optional, not getting total_iterations from trainer script)
"""
import argparse
import yaml
import imp
import os
import os.path as osp
from datetime import datetime
import sh
import socket
import random
import pprint

from pymongo import MongoClient

import logging
logging.basicConfig(level=logging.INFO,
    format='[%(levelname)s] %(asctime)s: %(name)s: %(message)s')
logger = logging.getLogger(__name__)

from email_server import EmailServer

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str, required=True,
                        help='Name of experiment config yaml file')
    # TODO make this better
    parser.add_argument('-p', '--mongo_password', type=str, required=False, default=None,
                        help='Password for mongo user for writing logs to db')
    # TODO add this
    # parser.add_argument('-s', '--snapshot', type=str, required=False,
    #                     help='Start an experiment from a snapshot')
    return parser.parse_args()

def setup_experiment_dir(config):
    """ Create the experiment output dir. """
    # user can override `results_`dir_name`
    # or they can optionally provide an additional prefix for the datatime dirname
    # or we will provide a defacto name
    dirname = ''
    if 'results_dir_prefix' in config:
        dirname += config['results_dir_prefix']
    if 'results_dir_name' in config:
        dirname += config['results_dir_name']
    else:
        timestamp = datetime.strftime(datetime.now(), '%b-%d-%Y-%H.%M.%f')
        dirname += '{}_experiment'.format(timestamp)

    snapshot_dir = osp.join(dirname, 'snapshots')
    tmpsnapshot_dir = osp.join(dirname, 'tmpsnapshots')
    if not osp.exists(dirname): os.makedirs(dirname)
    if not osp.exists(snapshot_dir): os.makedirs(snapshot_dir)
    if not osp.exists(tmpsnapshot_dir): os.makedirs(tmpsnapshot_dir)
    return dirname, timestamp

def commit(experiment_name):
    sh.git.commit('-a',
            m='"auto commit tracked files for new experiment: {}"'.format(experiment_name),
            allow_empty=True
        )
    commit_hash = sh.git('rev-parse', 'HEAD').strip()
    return commit_hash

def maybe_load_config(setup_config):
    """ Take a config object and do one of the following:

    * If `setup_config` is stringlike and is a yaml file,
      then load that as the config
    * If `setup_config` is a dictionary, then just pass that through.
    * Else complain.

    """
    if isinstance(setup_config, basestring):
        if setup_config.endswith('.yaml') and osp.exists(setup_config):
            return yaml.load(open(setup_config))
        else:
            logger.critical('Invalid configuration at {}'.format(setup_config))
            raise ValueError, 'Invalid configuration at {}:\n\
must be valid existing yaml'.format(setup_config)
    elif type(setup_config) is dict:
        return setup_config
    else:
        logger.critical('Invalid configuration in `setup_config`')
        raise ValueError, 'Invalid configuration in `setup_config`'

def import_module(module_name, setup_file):
    # todo handle specification of a module, not a file
    return imp.load_source(module_name, setup_file)

def setup_email_server():
    email_config = {
        "EMAIL_ORG": "@gmail.com",
        "FROM_UID":"chainer.monitor",
        "FROM_PWD": "Cha1nerM0nitor", #os.environ['CHAINER_MONITOR_PASSWORD'],
        "IMAP_SERVER":"imap.gmail.com",
        "SMTP_SERVER": "smtp.gmail.com",
        "SMTP_PORT": 587
    }
    return EmailServer(email_config)

def get_db(db_config):
    client = MongoClient('mongodb://{username}:{password}@{host}:{port}/{database}'.format(
        **db_config))
    db = client[db_config['database']]['config']
    return db

def run_experiment(config, mongo_password=None):
    full_config = config # config that will be output in results for reproducibility

    # setup random seed, email server, output dir, and commit the code
    random.seed(config['random_seed'])
    email_server = setup_email_server()
    full_config['pid'] = os.getpid()
    full_config['hostname'] = socket.gethostname()
    full_config['cwd'] = os.getcwd()
    results_dir, experiment_uid = setup_experiment_dir(config)
    full_config['results_dirname'] = results_dir
    full_config['uid'] = experiment_uid
    full_config['commit_hash'] = commit(results_dir)

    # get the database connection
    mongo_config = config['mongo_config']
    if mongo_password is None:
        mongo_password = os.environ['CHMON_MONGO_PASSWORD']
    if mongo_password is None:
        raise ValueError, "Mongo password must be passed or set at $CHMON_MONGO_PASSWORD"
    mongo_config['password'] = mongo_password
    db = get_db(mongo_config)

    try:
        # setup the dataset
        logger.info('Loading dataset')
        data_config = config['data_setup']
        data_setup_config = maybe_load_config(data_config['setup_config'])
        full_config['data_setup']['setup_config'] = data_setup_config

        data_setup_module = import_module('data_setup', data_config['setup_file'])
        data_setup_results = data_setup_module.setup(
            data_setup_config)

        # setup the model
        logger.info('Setting up models')
        model_config = config['model_setup']
        model_setup_config = maybe_load_config(model_config['setup_config'])
        full_config['model_setup']['setup_config'] = model_setup_config

        model_setup_module = import_module('model_setup', model_config['setup_file'])
        model_setup_results = model_setup_module.setup(
            model_setup_config, data_setup_results)

        # setup the trainer
        logger.info('Setting up training')
        trainer_config = config['trainer_setup']
        trainer_setup_config = maybe_load_config(trainer_config['setup_config'])
        trainer_setup_config['results_dirname'] = results_dir
        trainer_setup_config['experiment_uid'] = experiment_uid
        trainer_setup_config['mongo_config'] = mongo_config
        full_config['trainer_setup']['setup_config'] = trainer_setup_config

        trainer_setup_module = import_module('trainer_setup', trainer_config['setup_file'])
        trainer, total_iterations = trainer_setup_module.setup(
            trainer_setup_config, data_setup_results, model_setup_results)

        # save the full configuration
        logger.info('Saving experiment configuration')
        full_config['total_iterations'] = total_iterations
        full_config['start_time'] = datetime.now()
        full_config['finish_time'] = None
        # drop the db password before saving the config
        full_config['trainer_setup']['setup_config']['mongo_config'].pop('password', None)
        yaml.dump(full_config, open(osp.join(results_dir, 'full_config.yaml'),'w'))
        mongo_id = db.insert_one(full_config).inserted_id

        # run it
        logger.info('Running trainer')
        if 'email' in config:
            email_server.send_email(config['email'],
                                    '[CHAINER MONITOR] - {}'.format(results_dir),
                                    '<h3>Experiment {} has setup successfully and is starting</h3>\n\n\
Here is the configuration:\n\n<pre>{}</pre>'.format(results_dir, pprint.pformat(full_config)))
        trainer.run()

        # finish up
        logger.info('Finished Experiment')
        full_config['finish_time'] = datetime.now()
        db.update_one({'_id':mongo_id}, {"$set": full_config}, upsert=False)
        if 'email' in config:
            email_server.send_email(config['email'],
                                    '[CHAINER MONITOR] - {}'.format(results_dir),
                                    '<h3>Experiment {} has successfully finished</h3>'.format(results_dir))
    except Exception as e:
        logger.critical('FATAL EXCEPTION:\n{}'.format(e))
        if 'email' in config:
            email_server.send_email(config['email'],
                                    '[CHAINER MONITOR] - {}'.format(results_dir),
                                    '<h3>Exception:</h3>\n{}'.format(e))

if __name__ == '__main__':
    args = parse_args()
    config = yaml.load(open(args.config))
    run_experiment(config, args.mongo_password)
