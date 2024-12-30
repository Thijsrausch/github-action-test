def get_experiment_nodes(absolute_path_to_experiment):
    return [ #ast of script
            {
                'role': '',
                'variables': '',
                'image': '',
                'setup_script': {
                    'source': '',
                    'variables': [],
                    'tooling': '' #?
                    # what does it do? - check with chatgpt
                },
                'measurement_script': {
                    'source': '',
                    'variables': '',
                    'steps': [],

                    # what does it do? - check with chatgpt
                },
            }
        ], # hardware?