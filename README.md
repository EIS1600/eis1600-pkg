# EIS1600 Tools

## Installation
```shell
$ pip install eis1600
```

In case you have an older version installed, use

```shell
$ pip install --upgrade eis1600
```

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
```shell
$ disassemble_into_miu_files <uri>.EIS1600
```

Use the `-e` option to process all EIS1600 files from the TEXT repo. Must be run from the root of TEXT repo.
```shell
$ disassemble_into_miu_files -e <TEXT_repo>
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
