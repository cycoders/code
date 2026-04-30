#!/bin/bash

# Fixed: no eval, rm -i, grep log.txt, for i in dir/*, [ $var = foo ]

rm -i *

grep error log.txt

for i in dir/*; do
  echo "$i"
done

if [ "$var" = "foo" ]; then
  echo ok
fi