#!/bin/bash -x
ck-list-sessions

[ -z "${SESS}" ] && \
    SESS=$(ck-list-sessions | grep -B1000 "x11-display-device = '/dev/tty7'" | egrep -o ^Session[0-9]+ | tail -n1)

dbus-send --system --print-reply --dest="org.freedesktop.ConsoleKit" /org/freedesktop/ConsoleKit/"${SESS}" org.freedesktop.ConsoleKit.Session.Unlock
