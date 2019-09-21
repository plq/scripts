#!/bin/bash

# Put your fun stuff here.
export PYTHONDONTWRITEBYTECODE="x"
export PATH=$HOME/.local/bin:$PATH

function parse_git_branch {
   git branch --no-color 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/(\1) /'
}

export PS1="$PS1\$(parse_git_branch)"

#PERL_MB_OPT="--install_base \"/home/plq/perl5\""; export PERL_MB_OPT;
#PERL_MM_OPT="INSTALL_BASE=/home/plq/perl5"; export PERL_MM_OPT;
