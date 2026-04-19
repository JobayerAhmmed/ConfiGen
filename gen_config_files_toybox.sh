#!/bin/bash

mkdir -p generated

genconfig()
{
#   for j in $(ls toys/*/README | sort -s -r)
#   do
#     DIR="$(dirname "$j")"

#     [ $(ls "$DIR" | wc -l) -lt 2 ] && continue

#     echo "menu \"$(head -n 1 $j)\""
#     echo

    # for i in $(ls -1 $DIR/*.c)
  find "toys" -maxdepth 2 -type f -print | while read -r i;
    do
      echo "# $i"
      sed -n '/^\*\//q;/^config [A-Z]/,$p' $i || return 1
      echo
    done

    # echo endmenu
#   done
}

# We do not generate Config.probed file because the content for
# Config.probed is different in different times.
# i.e., in commit ed6ed62, there is only one config, TOYBOX_CONTAINER.
# In commit 03af0d1, there are two - TOYBOX_ON_ANDROID and TOYBOX_FORK
# probeconfig > generated/Config.probed || rm generated/Config.probed
genconfig > generated/Config.in || rm generated/Config.in
