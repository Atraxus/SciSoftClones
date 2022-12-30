# Script for running all the following tools:
# 1. CCFinderSW
# 2. Duplo
# 3. NiCad 6.0
# 4. PMD CPD

# Mode: preprocessed vs unpreprocessed
if [ "$1" = "-u" ]; then
    MODE="Unprocessed"
else
    MODE="Preprocessed"
fi


# 1. CCFinderSW
./CCFinderSW/bin/CCFinderSW d -d ./CodeBase/$MODE/ -l fortran -o ../BAScripts/Results/$MODE/out -t 25 -w 0 --ccfsw set

# 2. Duplo
./Duplo/duplo ./CodeBase/Files$MODE.txt ../BAScripts/Results/$MODE/out_duplo.txt

# 3. NiCad 6.0
# cd NiCad-Fortran
# ./nicad6 functions f90 ../CodeBase/$MODE/ > ../../BAScripts/Results/$MODE/log_nicad.txt
# cd ..

# 4. PMD CPD
./PMD/bin/run.sh cpd --minimum-tokens 25 --files ./CodeBase/$MODE/ --language fortran > ../BAScripts/Results/$MODE/out_pmd.txt
