#!/bin/sh
PROG=$(basename $0)

usage()
{
    echo "${PROG} <template-file> [ <config> ]"
}

expand()
{
    local template="$(cat $1)"
    eval "echo \"${template}\""
}

case $# in
    1) expand "$1";;
    2) . "$2"; expand "$1";;
    *) usage; exit 0;;
esac
