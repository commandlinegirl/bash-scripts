#!/usr/env/bin bash

# Read country names into an array 
countries=('')
while read country; do
   countries=("${countries[@]}" $country)
done

# Filter out all the names containing the letter 'a' or 'A'.
echo ${countries[@]/*[Aa]*/}

# Replace capital letters with a dot
echo ${countries[@]/[:A-Z:]/\.}

# Length of the element located at index 0
echo ${#countries[0]}

# Slice the array (display the elements between position 3 and 5, both inclusive
echo ${countries[@]:3:5}
