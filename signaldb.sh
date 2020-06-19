#!/bin/bash
sigBase="${HOME}/.config/Signal/";
key=$( /usr/bin/jq -r '."key"' ${sigBase}config.json );
db="${HOME}/.config/Signal/sql/db.sqlite";

/usr/bin/sqlcipher "$db" -cmd "PRAGMA key = \"x'"$key"'\""
