#!/bin/bash

TIME=`date +"%b-%d-%y"`             # This Command will add date in Backup File Name.
FILENAME="backup-$TIME.tar.gz"      # Here i define Backup file name format.
SRCDIR="."                  # Location of Important Data Directory (Source of backup).
DESDIR="./backup"            # Destination of backup file.

tar cpzf $DESDIR/$FILENAME --exclude="./stream/cache/*" --exclude="*.pyc" --exclude="*~" $SRCDIR
