def get_experiment_usage(ast):
        for node in ast:
            # If this is a command node, check if it's the echo usage line
            if node.kind == 'command':
                words = [p.word for p in node.parts if p.kind == 'word']
                if words and words[0] == 'echo':
                    command_text = ' '.join(words[1:])
                    if 'Usage:' in command_text:
                        return command_text.strip('"\'').replace("Usage: ", "", 1)

            # Not a command node, so we need to go deeper
            # Try known attributes that can hold child nodes
            for attr_name in ('parts', 'list', 'command_list'):
                child_nodes = getattr(node, attr_name, [])
                if child_nodes:
                    usage = get_experiment_usage(child_nodes)
                    if usage is not None:
                        return usage
        return None
