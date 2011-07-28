#!/usr/bin/python -tt
#
# Copyright (c) 2011, Burak Arslan <burak.arslan@arskom.com.tr>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Arskom Ltd. or Burak Arslan, nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import argparse
import os
import re

from sqlalchemy import sql
from sqlalchemy import create_engine
from sqlalchemy import MetaData

# shamelessly plagiarized from bpgsql
ESCAPE_CHARS = re.compile("[\x00-\x1f'\\\\\x7f-\xff]")
escape = lambda v2: ESCAPE_CHARS.sub(lambda x: '\\x%02x' % ord(x.group(0)), v2)


def main():
    parser = argparse.ArgumentParser(description='An awesomer pg_dump.')

    # pg_dump features
    parser.add_argument('--host', type=str, nargs=1, default='localhost',
                   help='database server host or socket directory')
    parser.add_argument('--port', '-p', type=int, nargs=1, default=5432,
                   help='database server port number')
    parser.add_argument('--username', '-U', type=str, nargs=1,
                   default=os.getlogin(),
                   help='connect as specified database user')
    parser.add_argument('dbname', type=str, nargs='*',
                   help='the name of the database')

    # extensions
    parser.add_argument('--filter', type=str, nargs=1, default="",
                   help='connect as specified database user')

    args = parser.parse_args()

    if args.dbname is None:
        args.dbname = args.username

    conn_str = 'postgres://%(username)s:@%(host)s:%(port)d/%(dbname)s' % {
        'username': args.username[0],
        'host': args.host,
        'port': args.port,
        'dbname': args.dbname[0],
    }

    #from IPython.Shell import IPShellEmbed
    #ipshell = IPShellEmbed([])

    engine = create_engine(conn_str)
    meta = MetaData()
    meta.reflect(bind=engine)

    for v in meta.sorted_tables:
        print args.filter

        cur = engine.execute(sql.select(v.c))

        for r in cur.fetchall():
            row_dict = dict(r)
            insert_str = unicode(v.insert(values=row_dict))

            for k2, v2 in row_dict.items():
                if v2 is None:
                    val = 'NULL'
                else:
                    try:
                        val = u"E'%s'" % escape(v2)
                    except:
                        val = u"'%s'" % v2

                insert_str = insert_str.replace(':%s' % k2, val)

            print insert_str.encode('utf8'), ';'

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
