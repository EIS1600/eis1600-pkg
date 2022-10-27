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

Use the -e option to process all files from the EIS1600 repo.
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

The MIU directory will be created next to the EIS1600 file.
```shell
$ disassemble_into_miu_files <uri>.EIS1600
```

Use the -e option to process all files from the EIS1600 repo.
```shell
$ disassemble_into_miu_files -e <EIS1600_repo>
```

### Reassembling

The MIU directory has to be next to the EIS1600 file.
```shell
$ reassemble_from_miu_files <uri>.EIS1600
```

Use the -e option to process all files from the EIS1600 repo.
```shell
$ reassemble_from_miu_files -e <EIS1600_repo>
```
