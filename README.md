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

Converts mARkdown file to EIS1600_tmp (without inserting UIDs).
The .EIS1600_tmp file will be created next to the .mARkdown file.
```shell
$ convert_mARkdown_to_Eis1600.py <uri>.mARkdown
```

EIS1600_tmp files do not contain UIDs yet, to insert UIDs run insert_uids.py on the .EIS1600_tmp file.
```shell
$ insert_uids.py <uri>.EIS1600_tmp
```

#### Batch processing of mARkdown files

Use the -e option to process all files from the EIS1600 repo.
```shell
$ convert_mARkdown_to_EIS1600.py -e <EIS1600_repo>
$ insert_uids.py -e <EIS1600_repo>
```

To process all mARkdown files in a directory, give an input AND an output directory.
Resulting .EIS1600_tmp files are stored in the output directory.
```shell
$ convert_mARkdown_to_EIS1600.py <input_dir> <output_dir>
$ insert_uids.py <input_dir> <output_dir>
```

### Disassembling

The MIU directory will be created next to the EIS1600 file.
```shell
$ disassemble_into_miu_files.py <uri>.EIS1600
```

Use the -e option to process all files from the EIS1600 repo.
```shell
$ disassemble_into_miu_files.py -e <EIS1600_repo>
```

### Reassembling

The MIU directory has to be next to the EIS1600 file.
```shell
$ reassemble_from_miu_files.py <uri>.EIS1600
```

Use the -e option to process all files from the EIS1600 repo.
```shell
$ reassemble_from_miu_files.py -e <EIS1600_repo>
```
