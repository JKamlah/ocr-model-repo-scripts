import json
import os
from pathlib import Path
from shutil import move

import typer
import yaml

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


@app.command(name="metadata")
def metadata(directory: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, readable=True)):
    """
    Processes JSON metadata files in a directory, converting them into HTML format.
    Args:
        directory (Path): The path to the directory containing JSON metadata files.
    """
    # Function to generate HTML content from the parsed JSON data
    def generate_html(data):
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

        html_content = f'''<div>
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

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().startswith('metadata') and (file.endswith('.json') or file.endswith('.json')):
                full_path = Path(root) / file
                # Parse the JSON data
                with open(full_path, 'r') as fin:
                    data = json.load(fin)

                # Generate HTML content
                html_result = generate_html(data)
                # Write Metadata md with html content
                with open(full_path.with_suffix('.md'), 'w') as fout:
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
        html_content = f'''<div>
   <h1 id="title">Welcome to our OCR-Model overview</h1>
   <p id="paragraph"> We are delighted to have you explore our collection of models. 
   Dive in and discover the perfect model that aligns with your goals and aspirations!</p>
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
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().startswith('metadata') and (file.endswith('.json') or file.endswith('.json')):
                full_path = Path(root) / file
                # Parse the JSON data
                with (open(full_path, 'r') as fin):
                    data = json.load(fin)
                    data['model']['defaultmodel'] = data['model']['defaultmodel'].replace('/blob/',
                                                                                          '/raw/') if 'github.com' in \
                                                                                    data['model']['defaultmodel'] else \
                    data['model']['defaultmodel']
                    model_table += f'''         <tr>
           <th><a href="{full_path.with_suffix('.md')}">{data['model']['name']}</a></th>
           <td>{data["software"]["name"]}</td>
           <td>{data['model']['type']}</td>
           <td>{data['model']['description']}</td>
           <td><a href="{data['model']['defaultmodel']}" download>Download</a><</td>
         </tr>'''
    if model_table != '''''':
        # Generate HTML content
        html_result = generate_html(model_table)
        # Write Metadata md with html content
        with open(Path('index.md'), 'w') as fout:
            fout.write(html_result)


if __name__ == "__main__":
    app()
