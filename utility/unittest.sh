#!/bin/bash
PATH_TO_SCRIPT=$(echo $PWD/${0##*/})
PATH_TO_FOLDER=`dirname "$PATH_TO_SCRIPT"`

export PYTHONPATH=$PYTHONPATH:$PATH_TO_FOLDER
cd $PATH_TO_FOLDER && py.test tests/unit
