#!/bin/bash
if [ -n "$1" ]; then
  echo "The output file is set to "$1
  output_file=$1
else
  echo "The output file is not provided, use output.csv as default"
  output_file="output.csv"
fi

rm $output_file

advTestSeq=$(seq 2 1 5)
itNoSeq=$(seq 0 5)

pipenv run python3 cmd.py --printHeader True >> $output_file

parallel pipenv run python3 cmd.py --scNo 1 --advNo {1} --simLen 100000000 --itNo {2} ::: $advTestSeq ::: $itNoSeq >> $output_file