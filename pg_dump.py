
import argparse
import os
import re

from sqlalchemy import sql
from sqlalchemy import create_engine
from sqlalchemy import MetaData


parser = argparse.ArgumentParser(description='An awesomer pg_dump.')

parser.add_argument('--host', type=str, nargs=1, default='localhost',
                   help='database server host or socket directory')
parser.add_argument('--port', '-p', type=int, nargs=1, default=5432,
                   help='database server port number')
parser.add_argument('--username', '-U', type=str, nargs=1, default=os.getlogin(),
                   help='connect as specified database user')
parser.add_argument('dbname', nargs='*', default=None, help='BAR!')

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

ESCAPE_CHARS = re.compile("[\x00-\x1f'\\\\\x7f-\xff]")
escape = lambda v2: ESCAPE_CHARS.sub(lambda x: '\\x%02x' % ord(x.group(0)), v2)

for v in meta.sorted_tables:
    cur = engine.execute(sql.select(v.c))

    for r in cur.fetchall():
        row_dict = dict(r)
        insert_str = unicode(v.insert(values=row_dict))

        for k2,v2 in row_dict.items():
            try:
                val = escape(v2)
            except:
                val = unicode(v2)

            insert_str = insert_str.replace(':%s' % k2, u"E'%s'" % val)

        print insert_str.encode('utf8'),';'
