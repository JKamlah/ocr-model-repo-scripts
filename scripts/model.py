import json
import os
import typer
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from shutil import move
from typing import Optional, Dict, Any

app = typer.Typer()


def convert_yaml_to_json(yaml_file: Path, json_file: Path):
    """
    Converts a single YAML file to a JSON file.
    """
    with open(yaml_file, 'r') as yf, open(json_file, 'w') as jf:
        yaml_content = yaml.safe_load(yf)
        json.dump(yaml_content, jf, indent=4)


@app.command(name="yaml2json")
def yaml_to_json(directory: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, readable=True)):
    """
    Finds all YAML files in the given directory (including subdirectories)
    and converts them to JSON files.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().startswith('metadata') and (file.endswith('.yml') or file.endswith('.yaml')):
                full_path = Path(root) / file
                json_path = full_path.with_suffix('.json')
                typer.echo(f"Converting {full_path} to {json_path}")
                convert_yaml_to_json(full_path, json_path)


@app.command(name="empty-readme")
def empty_readme():
    """
    Find README file saves a copy and create a new empty file.
    """
    path = Path('README.md')
    if path.exists():
        copy_path = Path('readme_old/')
        copy_path.mkdir(exist_ok=True)
        new_file = copy_path.joinpath(f"README.{len(list(copy_path.glob('*.md')))}.md")
        move(path, new_file)
    path.touch()


@app.command(name="readme")
def readme(directory: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, readable=True),
            title: str = typer.Option('', "--title", help="Title for the README"),
            gh_url: str = typer.Option('', "--gh-url", help="URL for the GitHub Pages")):
    """
    Processes JSON metadata files in a directory, converting them into HTML format.
    Args:
        directory (Path): The path to the directory containing JSON metadata files.
        title (str): Title information.
    """

    # Function to generate HTML content from the parsed JSON data

    @dataclass
    class Topic:
        state: Dict[str, Optional[bool]] = field(default_factory=lambda: {
            'Delete': None,
            'Title': None,
            'Description': None,
            'Metadata': None,
            'Models': None,
            'GitHub-Pages': None,
            'Acknowledgments': None
        })
        text: Dict[str, Optional[bool]] = field(default_factory=lambda: {
            'Delete': '',
            'Title': '## Title\n',
            'Description': '## 📚 Description\n',
            'Metadata': '## 📜 Metadata\n',
            'Models': '## 📂 Models\n',
            'GitHub-Pages': '## 🔖 **GitHub** Pages\n',
            'Acknowledgments': '## 👏 Acknowledgments\n'
        })

        def update_state(self, line: str):
            for key in self.state:
                if line.strip() in [f'<!-- {key} !-->', f'<!-- /{key} !-->']:
                    self.state[key] = line.strip() == f'<!-- {key} !-->'
                    return self.state[key]
            return False

        def reset_state(self, key: str):
            if self.state[key] is False:
                self.state[key] = None

        def state_active(self, key: str) -> bool:
            return self.state[key]

    # Path to README file
    readme_fpath = directory.joinpath('README.md')
    if not readme_fpath.exists():
        return

    topic = Topic()
    text_content = ""

    topic.text['Title'] = '## '+title if title != '' else topic.text['Title']
    topic.text['GitHub-Pages'] += f"You can also visit our **GitHub** Pages: {gh_url}" if gh_url != '' else topic.text[
        'GitHub-Pages']
    topic.text['Acknowledgments'] += (f"You may use and share the models under the terms of [LICENSE](LICENSE.md).\\\n"
                                      f"\\\n"
                                      f"This repository is based on:\\\n"
                                      f"* [OCR-Model-Repo-Template](https://github.com/UB-Mannheim/ocr-model-repo-template)")

    # Read information about all models
    if metadata_files := [fpath for fpath in directory.rglob('*') if fpath.name.lower().startswith('metadata.json')]:
        topic.text['Models'] += '|'.join(['Model', 'OCR-Engine', 'Type of model', 'Description', 'Default model'])+'\n'
        topic.text['Models'] += '|'.join(['---']*5)+'\n'
        software, model_types = [], []
        for full_path in metadata_files:
            # Parse the JSON data
            with open(full_path, 'r') as fin:
                data = json.load(fin)
            software.append(data['software']['name'])
            model_types.append(data['model']['type'])
            topic.text['Models'] += '|'.join([f"[{data['model']['name']}]({str(full_path.parent)[3:]})",
                                              data['software']['name'],
                                              data['model']['type'],
                                              data['model']['description'],
                                              f"<a href=\"{data['model']['defaultmodel']}\" download>Download</a>"])+'\n'
        topic.text['Description'] += f"This model repository {f'contains one model' if len(metadata_files) == 1 else f'contains {len(metadata_files)} models.'}.\n"
        topic.text['Metadata'] += (f"**Model software**: {' , '. join(set(software))}.\\\n"
                                   f"**Model types**: {' , '. join(set(model_types))}.\n")
    with open(readme_fpath, 'r') as file:
        for line in file:
            if topic.update_state(line) or any(topic.state.values()):
                continue
            for section, active in topic.state.items():
                if active is False:
                    if section != 'Delete':
                        text_content += f"\n<!-- {section} !-->\n{topic.text.get(section)}\n<!-- /{section} !-->\n"
                    topic.reset_state(section)
                    break
            else:  # This else belongs to the for-loop, not the if-statement
                text_content += line

    with open(readme_fpath, 'w') as file:
        file.write(text_content)

@app.command(name="metadata")
def metadata(directory: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, readable=True)):
    """
    Processes JSON metadata files in a directory, converting them into HTML format.
    Args:
        directory (Path): The path to the directory containing JSON metadata files.
    """

    # Function to generate HTML content from the parsed JSON data
    def generate_html(data, full_path):
        """
        Generates HTML content from parsed JSON data.
        Args:
            data (dict): A dictionary containing the metadata.
        Returns:
            str: A string of HTML content.
        """
        model = data["model"]
        training = data["training"]
        evaluation = data["evaluation"]
        license_info = f"{model['license']['name']} (see: {model['license']['url']})"

        authors = "".join(
            [f"<dd>{author['name']} {author['surname']} ({', '.join(author['roles'])}) (ORCID: {author['orcid']})</dd>"
             for author in data["authors"]])

        html_content = f'''<link rel="stylesheet" href="{''.join(['../'] * len(full_path.parent.parent.parts))}table_hide.css"/>
<div>
   <h1 id="title">{model["name"]}</h1>
   <p id="paragraph">{model["description"]}</p>
   <h2>Metadata</h2>
   <dl class="grid">
      <dt id="Language">OCR engine / software:</dt>
      <dd>{data["software"]["name"]}</dd>
      <dt id="Type">Model type:</dt>
      <dd>{model["type"]}</dd>
      <dt id="Format">Format:</dt>
      <dd>{model["fileformat"]}</dd>
      <dt id="Topology">Topology:</dt>
      <dd>{model["topology"]}</dd>
      <dt id="Creation">Creation:</dt>
      <dd>{model["creation-date"]}</dd>
      <dt id="License">License:</dt>
      <dd>{license_info}</dd>
   </dl>
   <h2>Training</h2>
   <dl class="grid">
      <dt id="Training-type">Type of training:</dt>
      <dd>{training["info"]["trainingstype"]}</dd>
      <dt id="Epochs">Epochs:</dt>
      <dd>{training["info"]["direct"]}</dd>
   </dl>
   <h2>Evaluation</h2>
   <dl class="grid">
      <dt id="Information">Information:</dt>
      <dd>{evaluation["input"]}</dd>
      <dt id="Metric">Metric:</dt>
      <dd>{evaluation["metrics"]}</dd>
      <dt id="Result">Result:</dt>
      <dd>{evaluation["results"]}</dd>
   </dl>
   <h2>Project</h2>
   <dl class="grid">
      <dt id="Project">Project:</dt>
      <dd>{data["project"]["name"]}</dd>
      <dt id="Project-URL">Project-URL:</dt>
      <dd>{data["project"]["homepage"]}</dd>
      <dt id="Project-URL">Project-URL:</dt>
      {authors}
   </dl>
   <h2>Usage</h2>
   <dl class="grid">
      <dt id="Usage-General">General:</dt>
      <dd>{data["uses"]["general"]}</dd>
   </dl>
</div>
'''
        return html_content

    for full_path in [fpath for fpath in directory.rglob('*') if fpath.name.lower().startswith('metadata.json')]:
        full_path_out = Path('../docs/').joinpath(str(full_path)[3:]).with_suffix('.md')
        full_path_out.parent.mkdir(parents=True, exist_ok=True)
        # Parse the JSON data
        with open(full_path, 'r') as fin:
            data = json.load(fin)

        # Generate HTML content
        html_result = generate_html(data, full_path)
        # Write Metadata md with html content
        with open(full_path_out, 'w') as fout:
            typer.echo(f"Convert {full_path} to {full_path_out}")
            fout.write(html_result)


@app.command(name="index")
def index(directory: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, readable=True)):
    """
    Generates an HTML index file from JSON metadata files in a directory.
    Args:
        directory (Path): The path to the directory containing JSON metadata files.
    """

    def generate_html(model_table):
        """
        Generates HTML content for the index page.
        Args:
            model_table (str): HTML string of model details to be included in the table.
        Returns:
            str: A string of HTML content for the index page.
        """
        html_content = f'''<link rel="stylesheet" href="table_hide.css"/>
<div>
   <h1 id="title">Welcome to the OCR-Model overview</h1>
   <p id="paragraph"> Dive in and explore the collection of models!</p>
   <h2>Overview</h2>
     <table id="table_id">
       <thead>
          <tr>
             <th style="position: sticky !important; left: 0 !important;">model</th>
             <th>OCR engine</th>
             <th>Type of model</th>
             <th>Description</th>
             <th>Default model</th>
         </tr>
       </thead>
       <tbody>
{model_table}
       </tbody>
    </table>
</div>
'''
        return html_content

    model_table = ''''''
    for full_path in [fpath for fpath in directory.rglob('*') if fpath.name.lower().startswith('metadata.json')]:
        # Parse the JSON data
        with (open(full_path, 'r') as fin):
            data = json.load(fin)
            data['model']['defaultmodel'] = data['model']['defaultmodel'].replace('/blob/',
                                                                                  '/raw/') if 'github.com' in \
                                                                                              data['model'][
                                                                                                  'defaultmodel'] else \
                data['model']['defaultmodel']
            model_table += f'''         <tr>
             
           <th><a href="{str(full_path.with_suffix(''))[3:]}" title="{data['model']['name']}">{data['model']['name']}</a></th>
           <td>{data["software"]["name"]}</td>
           <td>{data['model']['type']}</td>
           <td>{data['model']['description']}</td>
           <td><a href="{data['model']['defaultmodel']}" download>Download</a></td>
         </tr>'''
    if model_table != '''''':
        # Generate HTML content
        html_result = generate_html(model_table)
    else:
        html_result = (f"# Page Update Notice\n"
                       "This page does not contain any metadata files. Please add them according to the instructions and push a new version tag.\\\n"
                       "Stay tuned for updates!")
    # Write Metadata md with html content
    with open(Path('index.md'), 'w') as fout:
        typer.echo(f"Save {Path('index.md')}")
        fout.write(html_result)


if __name__ == "__main__":
    app()
