def is_command_node(node):
    return hasattr(node, 'kind') and node.kind == 'command'


def is_word_node(node):
    return hasattr(node, 'kind') and node.kind == 'word'


def host_name(arg):
    if arg == '$1':
        return "host one"
    elif arg == '$2':
        return "host two"
    return arg


def get_command_action(tokens):
    """
    Given a list of tokens from a command node,
    return a human-readable step/action if recognized, otherwise None.
    """
    if not tokens or tokens[0] != 'pos':
        return None

    # pos allocations ...
    if tokens[1] == 'allocations':
        # pos allocations free "$1"
        if tokens[2] == 'free' and len(tokens) == 4:
            return f"Free {host_name(tokens[3])}"
        # pos allocations allocate "$1" "$2"
        elif tokens[2] == 'allocate' and len(tokens) == 5:
            return f"Allocate {host_name(tokens[3])} and {host_name(tokens[4])}"
        # pos allocations variables "$1" file [--as-global/--as-loop]
        elif tokens[2] == 'variables':
            host_arg = host_name(tokens[3])
            var_file = tokens[4]
            if '--as-global' in tokens:
                return f"Load global variables from {var_file} into {host_arg}"
            elif '--as-loop' in tokens:
                return f"Load loop variables from {var_file} into {host_arg}"
            else:
                return f"Load variables from {var_file} into {host_arg}"

    # pos nodes ...
    elif tokens[1] == 'nodes':
        # pos nodes image "$1" debian-buster
        if tokens[2] == 'image' and len(tokens) == 5:
            return f"Set image of {host_name(tokens[3])} to {tokens[4]}"
        # pos nodes reset "$1"
        if tokens[2] == 'reset' and len(tokens) == 4:
            return f"Reboot {host_name(tokens[3])}"

    # pos commands ...
    elif tokens[1] == 'commands':
        # pos commands launch ...
        if tokens[2] == 'launch':
            infile = None
            if '--infile' in tokens:
                infile_index = tokens.index('--infile')
                if infile_index + 1 < len(tokens):
                    infile = tokens[infile_index + 1]
            if not infile:
                infile = "unknown script"

            last_token = tokens[-1]
            the_host = host_name(last_token) if last_token.startswith('$') else "some host"

            if '--loop' in tokens:
                return f"Run {infile} on {the_host} (loop mode)"
            else:
                return f"Run {infile} on {the_host}"

    return None


def traverse_ast(node):
    """Recursively traverse the AST to find command nodes and extract steps."""
    steps = []
    if is_command_node(node):
        # Extract tokens by looking for 'word' type children
        tokens = [part.word for part in getattr(node, 'parts', []) if is_word_node(part)]
        action = get_command_action(tokens)
        if action:
            steps.append(action)

    # Recurse into possible child properties
    for attr_name in ['parts', 'list', 'commands']:
        if hasattr(node, attr_name):
            for child in getattr(node, attr_name):
                steps.extend(traverse_ast(child))

    return steps


def get_experiment_steps(script_ast):
    steps = []
    for node in script_ast:
        steps.extend(traverse_ast(node))
    return {i+1: step for i, step in enumerate(steps)}
