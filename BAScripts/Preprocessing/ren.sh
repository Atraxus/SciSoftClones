# Rename all *.FOR to *.f90
for f in *.FOR; do
	mv -- "$f" "${f%.FOR}.f90"
done
