# EIS1600 Tools

## Workflow

(*so that we do not forget again...*)

1. Double-check text in the Google Spreadsheet; “tag” is as “double-checked” (Column **PREPARED**);
  - These double-checked files have been converted to `*.EIS1600` format
2. The names of these files are then collected into `AUTOREPORT.md` under **DOUBLE-CHECKED Files (XX) - ready for MIU**.
3. Running `disassemble_into_mius` takes the list from `AUTOREPORT.md` and disassembles these files into MIUs and stores them in the MIU repo.

## Process

1. Convert from mARkdown to EIS1600TMP with `convert_mARkdown_to_EIS1600`
2. Check the `.EIS1600TMP`
3. Run `insert_uids` on the checked `.EIS1600TMP`
4. Check again. If anything was changed in the EIS1600 file, run `update_uids`
5. After double-check, the file can be disassembled by `disassemble_into_miu_files data/<author>/<text>/<edition>.EIS1600`

## Installation
```shell
$ pip install eis1600
```

In case you have an older version installed, use

```shell
$ pip install --upgrade eis1600
```

## Set Up Virtual Environment and Install the EIS1600 PKG there

To not mess with other python installations, we recommend installing the package in a virual environment.
To create a new virtual environment with python, run:
```shell
python3 -m venv eis1600_env
```

**NB:** while creating your new virtual environment, you must use Python 3.7 or 3.8, as these are version required by CAMeL-Tools.

After creation of the environment it can be activated by:
```shell
source eis1600_env/bin/activate
```

The environment is now activated and the eis1600 package can be installed into that environment with pip:
```shell
$ pip install eis1600
```
This command installs all dependencies as well, so you should see lots of other libraries being installed. If you do not, you must have used a wrong version of Python while creating your virtual environment.

You can now use the commands listed in this README.

To use the environment, you have to activate it for **every session**, by:
```shell
source eis1600_env/bin/activate
```
After successful activation, your user has the pre-text `(eis1600_env)`.

Probably, you want to create an alias for the source command in your *alias* file by adding the following line:
```shell
alias eis="source eis1600_env/bin/activate"
```

Alias files:

- on Linux:
  - `~.bash_aliases`
- On Mac:
  - `.zshrc` if you use `zsh` (default in the latest versions Mac OS);

## Usage

### Covert mARkdown to EIS1600 files

Converts mARkdown file to EIS1600TMP (without inserting UIDs).
The .EIS1600TMP file will be created next to the .mARkdown file (you can insert .inProcess or .completed files as well).
This command can be run from anywhere within the text repo - use auto complete (`tab`) to get the correct path to the file.
Alternative: open command line from the folder which contains the file which shall be converted.
```shell
$ convert_mARkdown_to_EIS1600TMP <uri>.mARkdown
```

EIS1600TMP files do not contain UIDs yet, to insert UIDs run insert_uids on the .EIS1600TMP file.
This command can be run from anywhere within the text repo - use auto complete (`tab`) to get the correct path to the file.
```shell
$ insert_uids <uri>.EIS1600TMP
```

#### Batch processing of mARkdown files

Use the `-e` option to process all files from the EIS1600 repo.
```shell
$ convert_mARkdown_to_EIS1600 -e <EIS1600_repo>
$ insert_uids -e <EIS1600_repo>
```

To process all mARkdown files in a directory, give an input AND an output directory.
Resulting .EIS1600TMP files are stored in the output directory.
```shell
$ convert_mARkdown_to_EIS1600 <input_dir> <output_dir>
$ insert_uids <input_dir> <output_dir>
```

### Disassembling

Disassemble files into the MIU repo. MIU repo has to be next to TEXT repo.
Must be run from the root of TEXT repo, this will disassemble all files from the AUTOREPORT.
```shell
$ disassemble_into_miu_files
```
Give the relative path to a file to disassemble a singe file.
```shell
$ disassemble_into_miu_files data/<author>/<text>/<edition>.EIS1600
```

### Reassembling

Run inside MIU repo. Reassemble files into the TEXT repo, therefore, TEXT repo has to be next to MIU repo.
```shell
$ reassemble_from_miu_files <uri>.IDs
```

Use the `-e` option to process all files from the MIU repo. Must be run from the root of MIU repo.
```shell
$ reassemble_from_miu_files -e <MIU_repo>
```

### NER Annotation

NER annotation for persons, toponyms, misc and dates.

To annotate all MIU files of a text give the IDs file as argument.
Can be used with `-p` option to run in parallel.
```shell
$ ner_annotate_mius <uri>.IDs
```

To annotate an individual MIU file, give MIU file as argument.
```shell
$ ner_annotate_mius <uri>/MIUs/<uri>.<UID>.EIS1600
```

Use the `-e` option to process all files from the MIU repo. Can be used with `-p` option for parallelization.
```shell
$ ner_annotate_mius -p -e <MIU_repo>
```
