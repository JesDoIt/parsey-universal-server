#!/usr/bin/env bash
languages=(
  "Chinese"
  "English"
  "Swedish"
)
for lang in "${languages[@]}"
do
  curl http://download.tensorflow.org/models/parsey_universal/$lang.zip -o $lang.zip
  unzip $lang.zip
  rm $lang.zip
done
