#!/bin/sh
SRCDIR=`pwd`

# Folder required for the bot to actually save lua code
mkdir luacode

# Makes luap
cd ./luapc
make
cd $SRCDIR

