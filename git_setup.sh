#!/bin/bash -x

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

git config --global user.name "Burak Arslan"
git config --global user.email "burak.arslan@arskom.com.tr"
git config --global core.pager ''
git config --global color.ui true
git config --global core.excludesfile "$DIR/global_ignores"
