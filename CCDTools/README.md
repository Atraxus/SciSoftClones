# CCDTools
Here you can find all tools used to generate results with the addition of NiCad. All changes I made are in the respective folders. To reproduce the results, you can simply add the tools (locally) to their folders and execute the run.sh script.

- https://pmd.github.io/latest/pmd_userdocs_cpd.html
- https://github.com/YuichiSemura/CCFinderSW
- https://github.com/dlidstrom/Duplo
- https://www.txl.ca/txl-nicaddownload.html

## How to execute
In this section, I list how the tools where executed and what needs to be taken into account, to get optimal results. All of the following commands will be for the proprocessed code base. This was applied analogous to the unprocessed code base.

### CCFinderSW
You can follow along the CLI outputs for configuring CCFinderSW.

In RAY-UI's case:
```
./CCFinderSW d -d ~/Documents/Uni/CCDTools/CodeBase/Preprocessed/ -l fortran -o ~/Documents/Uni/CCDTools/Results/Preprocessed/out -t 25 -w 0 --ccfsw set
```


### Duplo
From the man page:
```
./duplo [OPTIONS] [INTPUT_FILELIST] [OUTPUT_FILE]
```
In RAY-UI's case:
```
./duplo /home/maierjan/Documents/Uni/CCDTools/CodeBase/FilesPreprocessed.txt /home/maierjan/Documents/Uni/CCDTools/Results/Preprocessed/DuploOut.txt
```

Duplo per default searches for clones with:
 - minimum 4 lines per clone
 - minimum 3 characters per line
 - 100% similarity


### NiCad

Versions: TXL v10.8b, NiCad Clone Detector v6.2 (13.11.20)


From the man page:
```
Usage:  NiCad granularity language systems/systemdir [ config ]
          where granularity is one of:  { functions blocks ... }
          and   language    is one of:  { c java cs py ... }
          and   config      is one of:  { blindrename ... }
```
In RAY-UI's case:
```
./nicad6 functions f90 ~/Documents/Uni/CCDTools/CodeBase/Preprocessed/
```

Default config includes:
 - blind-renaming
 - similarity threshold of 70%
 - min. clone size 25 tokens and max. clone size 2500 tokens


### PMD CPD
Example from the documentation (website):
```
./run.sh cpd --minimum-tokens 100 --files /path/to/c/source --language cpp
```
In RAY-UI's case:
```
./run.sh cpd --minimum-tokens 25 --files ~/Documents/Uni/CCDTools/CodeBase/Preprocessed/ --language fortran
```

