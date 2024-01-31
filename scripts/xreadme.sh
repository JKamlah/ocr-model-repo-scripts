#!/bin/bash

file=README.md
if [ -f "$file" ];
then
    mv README.md README.xml
else
	echo "<empty>no Data</empty>" > README.xml

fi