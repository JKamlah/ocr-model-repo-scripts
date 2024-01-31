<img src="./img/ocr-model.png" width="200" align="right">

# ocr-model-repo-scripts

## Description
Python scripts and shell scripts for analyzing and creating GitHub pages of an ocr model repository. 
These are centrally managed and can be used by all repositories created with ocr-model-repo-template (https://github.com/UB-Mannheim/ocr-model-repo-template).

The format of the output files:
- Markdown,
- ruleset (JSON)
- Shell scripts

## Install with poetry

```shell
  python3 -m pip install poetry // sudo apt get install python3-poetry
  poetry install
  poetry shell
```

## Overview of scripts or programs

**🚀 ocr-model-repo.py **

   - **Environment parameters group**
        - Analysis of models metadata, GitHub page creation, following parameters are to be followed. Use environment variables https://docs.github.com/en/actions/learn-github-actions/environment-variables
            - repoBase=$GITHUB_REF_NAME
            - repoName=$GITHUB_REPOSITORY
            - bagitDumpNum=$GITHUB_RUN_NUMBER    
        
   - **Output parameter group:**
        - Specifies what type of analysis and in what form it should be displayed.
            - output=metadata -> transform METADATA
            - output=overview -> detailed table view

   - **Metadata parameter group:**
        - indicates that a metadata set is created for the models and the README and the README file is adapted.
            - directory = path to the main directory
     - **:wrench: general program call** (with active poetry shell)
        - ```shell
          ocr-model-repo-script metadata /path/to/directory/
          ```

**🚀 readmefolder.sh**
   - Archiving the original README file to the `readme_old` folder
     - **:wrench: general program call**
       - ```shell
           sh scripts/readmefolder.sh
         ```

**🚀 xreadme.sh**
   - Determination of the README file and change of the filename extension from Markdown to XML
     - **:wrench: general program call**
       - ```shell
           sh scripts/xreadme.sh
         ```
**🚀 lang.js**
   - Javascript for the automated language conversion (German/English) of the level description and the links to the OCR-D-GT Guidelines.
     
**🌻 table_hide.css**
   - CSS stylesheet to customize the formatting of GH pages. The GH pages use the dinky template (https://pages-themes.github.io/dinky/).

**🌻 levelparser.css**
   - CSS stylesheet for customising the formatting of GH pages, in particular for determining the transcription and structure levels.
