#!/usr/env/bin bash

# Read country names into an array and then filter out all 
# the names containing the letter 'a' or 'A'.

countries=('')
while read country; do
   countries=("${countries[@]}" $country)
done

echo ${countries[@]/*[Aa]*/}

