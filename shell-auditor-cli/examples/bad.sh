#!/bin/sh

eval "$USER_INPUT"

rm *

cat log.txt | grep error

for i in $(ls dir); do
  echo "$i"
done

if [[ $var == "foo" ]]; then
  echo ok
fi