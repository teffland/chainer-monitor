from __future__ import print_function
import argparse
import os
import os.path as osp
import json
import yaml
from pymongo import MongoClient
import numpy as np

from flask import Flask, render_template, render_template_string, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)
# api = Api(app)

@app.route('/', methods=['GET'])
def root():
    return render_template('index.html')

@app.route('/<path:path>', methods=['GET'])
def any_root_path(path):
    return render_template('index.html')

@app.route('/api', methods=["GET"])
def api_root():
    return render_template_string('<h1>API Whaa!</h1>')

@app.route('/api/experiment-names', methods=["GET"])
def experiments_names():
    if MODE == 'FILE':
        experiment_names = [ name for name in os.listdir(experiment_dir)
                             if osp.isdir(osp.join(experiment_dir, name)) ]
    else: # MODE IS MONGO
        experiment_names = db.config.distinct("uid")
    return jsonify(sorted(experiment_names))

@app.route('/api/experiment/<name>', methods=["GET"])
def experiment(name):
    if MODE == 'FILE':
        config = yaml.load(open(osp.join(experiment_dir, name, 'full_config.yaml'))),
        log = json.load(open(osp.join(experiment_dir, name, 'log')))
    else: # MODE IS MONGO
        config = db.config.find_one({'uid':name})
        config['_id'] = str(config['_id'])
        log = db.log.find({'uid':name}).sort('iteration')

    processed_log = process_log(log)
    # print(processed_log)
    data = {'config': config}
    data.update(processed_log)
    if data['log']:
        timing = {}
        timing['elapsed_time'] = max([datum['elapsed_time'] for datum in data['log']])
        timing['examples/sec'] = float(data['elapsed_examples'])/timing['elapsed_time']
        timing['elapsed_iterations'] = max([datum['iteration'] for datum in data['log']])
        timing['iterations/sec'] = float(len(data['log']))/timing['elapsed_time']
        timing['estimated_total_time'] = config['total_iterations'] / timing['iterations/sec']
        data['timing'] = timing
    else:
        timing = {}
        timing['elapsed_time'] = 0
        timing['examples/sec'] = 0
        timing['elapsed_iterations'] = 0
        timing['iterations/sec'] = 0
        timing['estimated_total_time'] = 0
        data['timing'] = timing
    return jsonify(data)

def process_log(log_iter):
    scalars = {}
    monitored_vars = {}
    log = []

    n_example = 0
    key_set = set()
    for i, entry in enumerate(log_iter):
        n_example += entry['n_examples']
        entry.pop('_id', None)
        key_set |= set(entry.keys())
        log.append(entry)

        # complile the log values into scalar sets and hists based on naming
        x_keys = ['iteration', 'n_examples', 'epoch']
        seen_vars = []
        for name, val in entry.items():
            if name in x_keys: continue # skip x keys
            key, attr = tuple(name.split(":")) if ":" in name else(name, "value")

            # scalars are those with just "value"
            if attr == "value":
                if not hasattr(val, '__len__'): # skip nonscalars
                    datum = {'y':val}
                    datum.update({xkey:entry[xkey] for xkey in x_keys})
                    if key not in scalars:
                        scalars[key] = [datum]
                        print("New Scalar Key: {}".format(key))
                        print("and its datum: {}".format(datum))
                    else:
                        scalars[key].append(datum)

            # everything else are monitored vars
            else:
                var_name = "/".join(key.split('/')[:-1])
                if var_name in seen_vars: continue
                seen_vars.append(var_name)

                # assemble the variable report datum and add it
                if var_name not in monitored_vars:
                    datum = {}
                    if var_name+"/data:hist_vals" in entry:
                        datum.update({"params": {
                            "histEdges":entry[var_name+"/data:hist_edges"],
                            "histVals":entry[var_name+"/data:hist_vals"]
                        }})
                    if var_name+"/grad:hist_vals" in entry:
                        datum.update({"grads": {
                            "histEdges":entry[var_name+"/grad:hist_edges"],
                            "histVals":entry[var_name+"/grad:hist_vals"]
                        }})
                    if var_name+"/update:hist_vals" in entry:
                        datum.update({"updates": {
                            "histEdges":entry[var_name+"/update:hist_edges"],
                            "histVals":entry[var_name+"/update:hist_vals"]
                        }})
                    print("New MonitoredVar Key: {}".format(var_name))
                    monitored_vars[var_name] = [datum]
                else:
                    datum = {}
                    if var_name+"/data:hist_vals" in entry:
                        datum.update({"params": {
                            "histVals":entry[var_name+"/data:hist_vals"]
                        }})
                    if var_name+"/grad:hist_vals" in entry:
                        datum.update({"grads": {
                            "histVals":entry[var_name+"/grad:hist_vals"]
                        }})
                    if var_name+"/update:hist_vals" in entry:
                        datum.update({"updates": {
                            "histVals":entry[var_name+"/update:hist_vals"]
                        }})
                    monitored_vars[var_name].append(datum)
                monitored_vars[var_name][-1].update({xkey:entry[xkey] for xkey in x_keys})

    # print('Keys: {}'.format("\n".join(list(key_set))))
    ret = {
        'log':log,
        'scalars':scalars,
        'monitored_vars':monitored_vars,
        'elapsed_examples': n_example
    }
    # compiled = {}
    # for entry in log:
    #     for name,val in entry.items():
    #         key, attr = tuple(name.split(":")) if ":" in name else (name, "value")
    #         print(name)
    #         if key not in compiled:
    #             compiled[key] = {}
    #         if attr not in compiled[key]:
    #             compiled[key][attr] = [val]
    #         else:
    #             compiled[key][attr].append(val)
    # return compiled
    return ret

def parse_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--experiment_dir', type=str, required=False, default=None,
                        help='Path to the directory containing the experiments')
    group.add_argument('-p', '--mongo_password', type=str, required=False, default=None,
                        help='Password for mongo user for writing logs to db')
    return parser.parse_args()

def get_db(db_config):
    client = MongoClient('mongodb://{username}:{password}@{host}:{port}/{database}'.format(
        **db_config))
    db = client[db_config['database']]
    return db

if __name__ == '__main__':
    args = parse_args()
    if getattr(args, 'experiment_dir'):
        globals()['MODE'] = 'FILE'
        globals()['experiment_dir'] = args.experiment_dir
    else:
        globals()['MODE'] = 'MONGO'
        mongo_config = yaml.load(open('mongo_config.yaml'))
        mongo_config['password'] = args.mongo_password
        globals()['db'] = get_db(mongo_config)
    app.run(host="localhost", port=9000, debug=True)
