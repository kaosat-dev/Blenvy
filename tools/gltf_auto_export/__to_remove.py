

def did_export_parameters_change(current_params, previous_params):
    set1 = set(previous_params.items())
    set2 = set(current_params.items())
    difference = dict(set1 ^ set2)
    
    changed_param_names = list(set(difference.keys())- set(AutoExportGltfPreferenceNames))
    changed_parameters = len(changed_param_names) > 0
    return changed_parameters