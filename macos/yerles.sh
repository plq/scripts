#!/bin/bash -x
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"; #"
ROOT=$(sudo -H bash -c 'echo $HOME')
[ -z "$ROOT" ] && exit 10
shopt -s dotglob
echo 'source $HOME/.bash_profile' > $HOME/.bashrc
echo "export PS1='\[\033]0;\u@\h:\w\007\]\[\033[01;32m\]\u@\h\[\033[01;34m\] \w \$\[\033[00m\] '" > $HOME/.bash_profile
sudo cp -vf $DIR/etc/* /etc || exit 20
sudo cp -vf $DIR/root/* $ROOT || exit 30
