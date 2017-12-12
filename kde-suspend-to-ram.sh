#!/bin/bash

dbus-send --print-reply --dest='org.freedesktop.ScreenSaver' /org/freedesktop/ScreenSaver org.freedesktop.ScreenSaver.Lock

sleep 1;
echo mem > /sys/power/state
