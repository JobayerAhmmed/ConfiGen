#!/bin/sh

export LC_ALL=C

srctree="$1"

status() { printf '  %-8s%s %s\n' "$1" "$2"; }
gen() { status "GEN" "$@"; }
chk() { status "CHK" "$@"; }

generate()
{
	# NB: data to be inserted at INSERT line is coming on stdin
	src="$1"
	dst="$2"
	header="$3"
	#chk "${dst}"
	{
		# Need to use printf: different shells have inconsistent
		# rules re handling of "\n" in echo params.
		printf "%s\n" "${header}"
		# print everything up to INSERT line
		sed -n '/^INSERT$/ q; p' "${src}"
		# copy stdin to stdout
		cat
		# print everything after INSERT line
		sed -n '/^INSERT$/ {
		:l
		    n
		    p
		    bl
		}' "${src}"
	} >"${dst}.tmp"
	if ! cmp -s "${dst}" "${dst}.tmp"; then
		gen "${dst}"
		mv "${dst}.tmp" "${dst}"
	else
		rm -f "${dst}.tmp"
	fi
}

# (Re)generate */Config.in
# We skip .dotdirs - makes git/svn/etc users happier
{ cd -- "$srctree" && find . -type d ! '(' -name '.?*' -prune ')'; } \
| while read -r d; do
	d="${d#./}"
	src="$srctree/$d/Config.src"
	dst="$d/Config.in"
	if test -f "$src"; then
		mkdir -p -- "$d" 2>/dev/null

		sed -n 's@^//config:@@p' "$srctree/$d"/*.c \
		| generate \
			"${src}" "${dst}" \
			"# DO NOT EDIT. This file is generated from Config.src"
	fi
done

# Last read failed. This is normal. Don't exit with its error code:
exit 0
