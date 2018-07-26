#!/bin/bash

echo
echo "*** Configuring run_farseer_gui.sh file..."
echo
tee run_farseer_gui.sh <<< \
"#!/usr/bin/env bash

export FARSEER_ROOT=\"$(pwd)\"
export PYTHONPATH=\$PYTHONPATH:\${FARSEER_ROOT}

python \$FARSEER_ROOT/gui/main.py \$*
"
chmod u+x run_farseer_gui.sh

echo
echo "*** Configuring run_farseer_commandline.sh file..."
echo
tee run_farseer_commandline.sh <<< \
"#!/usr/bin/env bash

export FARSEER_ROOT=\"$(pwd)\"
export PYTHONPATH=\$PYTHONPATH:\${FARSEER_ROOT}

python \$FARSEER_ROOT/core/farseermain.py \$*
"
chmod u+x run_farseer_commandline.sh

echo "*** Done..."
echo
echo \
"
    run_farseer_gui.sh and run_farseer_commandline.sh have been created.
    you may wish to complete this file with
    the necessary EXPORTS according to your Python setup.
    
    TO RUN FARSEER-NMR GUI:
    
    ./run_farseer_gui.sh
    
    or double click on the file :-)
"