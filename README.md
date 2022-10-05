# EIS1600 Tools

## Installation
```
$ pip install eis1600
```

## Usage

### Covert mARkdown to EIS1600 files

Execute inside the directory where the respective .mARkdown file is stored.
The .EIS1600_tmp file will be created next to the .mARkdown file.
```shell
$ cd <uri>
$ convert_mARkdown_to_Eis1600.py <uri>.mARkdown
```

EIS1600_tmp files do not contain UIDs yet, to insert UIDs run insert_uids on the .EIS1600_tmp file.
```shell
$ insert_uids.py <uri>.EIS1600_tmp
```

#### Batch processing of mARkdown files

To process all mARkdown files in a directory, give an input AND an output directory.
Resulting .EIS1600_tmp files are stored in the output directory.
```shell
$ convert_mARkdown_to_EIS1600.py <input_dir> <output_dir>
```

These files do not contain UIDs yet, to insert UIDs run insert_uids on the output directory.
```shell
$ insert_uids.py <input_dir> <output_dir>
```

### Disassembling

Execute inside the directory where the respective .EIS1600 file is stored.
The MIU directory will be created inside the current directory
```shell
$ cd <uri>
$ disassemble_into_miu_files.py <uri>.EIS1600
```

### Reassembling

Execute inside the directory where the respective .EIS1600 file is stored.
The MIU directory has to be under the current directory
```shell
$ cd <uri>
$ reassemble_from_miu_files.py <uri>.EIS1600
```
