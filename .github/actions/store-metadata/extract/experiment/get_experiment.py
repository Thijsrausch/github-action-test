import os
import sys
import bashlex

from extract.experiment.get_experiment_nodes import get_experiment_nodes
from extract.experiment.get_experiment_steps import get_experiment_steps
from extract.experiment.get_experiment_usage import get_experiment_usage
from utils.get_bash_script_ast import get_bash_script_ast

# Define mappings for commands to textual actions
# could come from the POS documentation

command_mappings = {
    "pos allocations free": "free hosts",
    "pos allocations allocate": "allocate {}",
    "pos nodes image": "set image for {} to Debian buster",
    "pos allocations variables": "load variable files",
    "pos nodes reset": "reboot experiment hosts",
    "pos commands launch": "launch experiments",
}

# Helper to resolve arguments to human-readable names
argument_mapping = {
    "$1": "node one",
    "$2": "node two",
}


def get_experiment(absolute_path_to_experiment):
    script_source = absolute_path_to_experiment + "/experiment/experiment.sh"
    script_ast = get_bash_script_ast(script_source)

    experiment = {
        'steps': [], # ast of script
        'source': script_source,
        'usage': '', # ast of script
        'nodes': []
    }

    experiment_steps = get_experiment_steps(script_ast)
    experiment["steps"] = experiment_steps if experiment_steps else None

    experiment_usage = get_experiment_usage(script_ast)
    experiment["usage"] = experiment_usage if experiment_usage else None

    experiment_nodes = get_experiment_nodes(absolute_path_to_experiment)
    experiment["nodes"] = experiment_nodes

    return experiment
