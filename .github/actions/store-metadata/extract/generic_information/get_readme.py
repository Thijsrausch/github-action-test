import re
import json
import os


# TODO - fix this

def parse_readme(absolute_path_to_repository):
    readme_dir = os.path.join(absolute_path_to_repository, 'README.md')

    with open(readme_dir, 'r', encoding='utf-8') as f:
        content = f.read()

    # Initialize a dictionary to store extracted data
    readme_data = {
        "title": "",
        "sections": []
    }

    # Extract the title (assumes the title is the first line and starts with a '#')
    title_match = re.match(r'^# (.+)', content)
    if title_match:
        readme_data["title"] = title_match.group(1)

    # Split by sections based on markdown headers (## Header)
    sections = re.split(r'\n## ', content)

    # First section is the description (if not empty)
    if sections[0].strip():
        readme_data["description"] = sections[0].strip()

    # Process each section and store in the JSON structure
    for section in sections[1:]:
        header_match = re.match(r'([^\n]+)\n(.+)', section, re.DOTALL)
        if header_match:
            section_title = header_match.group(1).strip()
            section_content = header_match.group(2).strip()
            readme_data["sections"].append({
                "title": section_title,
                "content": section_content
            })

    return readme_data
