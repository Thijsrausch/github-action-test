import bashlex


def get_bash_script_ast(absolute_path_to_script):
    with open(absolute_path_to_script, 'r', encoding='utf-8') as f:
        script_content = f.read()

    return bashlex.parse(script_content)
