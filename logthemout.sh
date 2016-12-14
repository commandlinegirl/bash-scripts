#!/bin/sh
# Log me out of all my current sessions

for t in `who | grep $USER | awk '{ print $2; }'`; do
  if [ `tty | grep $t | wc -l` -eq 0 ]; then
    echo "1"
    for p in `ps -au | awk '{ print $1" tty"$7" "$2" "$11; }' | grep $USER | grep bash | grep $t | awk '{ print $3; }'`; do
      echo "2"
      echo -n "Sending KILL signal to process $p..."
      kill -9 $p
      echo killed.
    done
  fi
done
