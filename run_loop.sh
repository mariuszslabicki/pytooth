#!/bin/bash
if [ -n "$1" ]; then
  echo "The output file is set to "$1
  output_file=$1
else
  echo "The output file is not provided, use output.csv as default"
  output_file="output.csv"
fi

rm $output_file

pipenv shell
first_run=true
for advNo in 10 20 30
do
    for itNo in {0..9}
    do
        echo "Advno "$advNo" iteration " $itNo
        if [ "$first_run" = true ] ; then
            python3 cmd.py --scNo 1 --advNo $advNo --simLen 100000000 --itNo $itNo >> $output_file
            first_run=false
        else
            python3 cmd.py --scNo 1 --advNo $advNo --simLen 100000000 --itNo $itNo | sed -n '2 p' >> $output_file
        fi
    done
done