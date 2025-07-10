#
# This hook expects global, scalar input features in json format. 
# Training: A file xxx_inp.json must exist next to each xxx.h3d.
# Prediction: A file predict_inp.json must exist in my_project/_hooks/
#

import os
import numpy as np
import json
from eds.physicsai import hooks
from eds.physicsai.dataset import ModelData

class global_inputs_hook(hooks.DataHook):
    @staticmethod
    def extract_hierarchy(caedata,**kwargs):
        return caedata

    @staticmethod
    def extract_model(run,**kwargs):
        _, ext = os.path.splitext(run.file)
        if ext in ['.fem', '.rad']:
            # we must be predicting
            hooksdir, _ = os.path.split(__file__)
            json_file = os.path.join(hooksdir, '_predict_inp.json')

        else:
            # we must be training
            json_file = run.file.replace(ext, '_inp.json')
            
        if not os.path.exists(json_file):
            print("The global inputs hook expected to find the file {}".format(json_file))
            return run
                
        with open(json_file, 'r') as f:
            js_data = json.load(f)

        # create model data from each of the global inputs
        for gi in js_data:
            if not _is_valid_entry(gi):
                continue

            # create a new dataset by assing the global input value to all nodes
            nodes = run.model.mesh.nodes
            md = ModelData( model  = run.model, 
                            keys   = nodes.keys(), 
                            values = np.expand_dims(np.repeat(gi['data'][0], len(nodes)), axis=-1), 
                            label  = gi['label'], 
                            attr   = {'bind':"ETYPE_NODE"})

            run = _append_model_data(run, md)

        return run

# helpers
def _append_model_data(run, md):
    # model_data starts off an an immutable list and we change it to a normal one
    if type(run.model.model_data)==type(list()):
        run.model.model_data.append(md)
    else:
        run.model.model_data = [md]

    return run

def _is_valid_entry(gi):
    for field in ['label', 'data']:
        if field not in gi:
            print("Each entry in the json file is expected to have the field {}".format(field))
            return False

    if len(gi['data']) != 1:
        print("This hook expects inputs to be scalars (length=1). The length of {} is {}".format(gi['label', len(gi['data'])]))
        return False

    try:
        float(gi['data'][0])
    except:
        print("This hook expects numerical data values. The type of {} is {}".format(gi['label'], type(gi['data'][0])))
        return False
    
    return True

hooks.data.add(global_inputs_hook)
