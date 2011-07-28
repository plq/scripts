#!/usr/bin/python -tt

#
# Migration script from dbmail 2.2.x message store to a maildir message store
# with dovecot extensions.
#
# Tested with dbmail-2.2.17 -> dovecot-2.0.13 on postgresql-9.0.4
# and sqlalchemy-0.7.1.
#

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
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 


#
# you neeed to have
#
#     pop3_uidl_format = %f
#
# in dovecot configuration to preserve pop3 uids.
#

#
# The dovecot-uidlist file output is version 1, whereas dovecot 2.0 uses version
# 3. The file is automatically migrated to version 3 on folder access.
# That's why this migration script should be run when dovecot is not running.
#

#
# Empty messages can appear in dovecot store if a message is deleted in dbmail
# store. It's recommended to run this script after running:
#
#     dbmail-util -ay
#
# command twice and while dbmail daemons are not running.
#

MAIL_ROOT = 'mail' # path to your dovecot mail store

# See: http://www.sqlalchemy.org/docs/core/engines.html#database-urls
DB_URI = 'postgres://postgres:@localhost:5432/dbmail' # The uri of your dbmail
                                                      # mail store

import re
def thous(x):
    return re.sub(r'(\d{3})(?=\d)', r'\1,', str(x)[::-1])[::-1]

import sys
import os
from time import mktime, time
from cStringIO import StringIO

from sqlalchemy import create_engine

def create_maildir(name):
    try:
        os.makedirs(name)
        os.makedirs(name+'/cur')
        os.makedirs(name+'/new')
        os.makedirs(name+'/tmp')

    except Exception, e:
        pass

engine = create_engine(DB_URI)
if len(sys.argv) > 1:
    users = engine.execute("select * from dbmail_users where userid in " + repr(tuple(sys.argv[1:])).replace(',)',')'))

else:
    users = engine.execute("select * from dbmail_users where user_idnr > 3") # first three users are for dbmail internal use

user_num = 0
global_size = 0

print "Migrating", users.rowcount, 'users.'
for user in users:
    user_num += 1
    user_size = 0
    print '(' + str(user.user_idnr) + ') \033[94m' +  user.userid + '\033[0m', user_num, '/', users.rowcount

    MAILDIR = "%s/%s/%s/.maildir/" % (MAIL_ROOT, user.userid.split('@')[1], user.userid.split('@')[0])
    mailboxes = engine.execute("select * from dbmail_mailboxes where owner_idnr = %s ", user['user_idnr'])
    create_maildir(MAILDIR)
    subs = set()

    mailboxes = mailboxes.fetchall()
    maxlen = 0
    maxlen = max([len(a.name) for a in mailboxes])

    max_id_cur = engine.execute(
        "select mbox.name, max(msg.message_idnr) as max "
        "from dbmail_mailboxes mbox "
        "     join dbmail_messages msg on msg.mailbox_idnr=mbox.mailbox_idnr "
        "where owner_idnr = %s "
        "group by mbox.name", user.user_idnr)

    max_ids={}
    for m in max_id_cur:
        max_ids[m.name.replace('/','.')] = m.max +1

    for mailbox in mailboxes:
        totalmessages = 0

        # fix the subdirectories
        mailbox_name = mailbox['name'].replace("/", ".")

        # create directory
        if mailbox_name == 'INBOX':
            mailbox_dir = MAILDIR
        else:
            mailbox_dir = MAILDIR + "." + mailbox_name

        mailbox_dir = mailbox_dir.replace('.INBOX/','')
        create_maildir(mailbox_dir)

        # set subscription
        subs.add( ("." + mailbox_name).strip(".") )

        if not (mailbox_name in max_ids): 
            continue

        f_uid = open(mailbox_dir + '/' + 'dovecot-uidlist','w')
        f_uid.write('1 ')
        f_uid.write(str(mailbox.mailbox_idnr))
        f_uid.write(' ')
        f_uid.write(str(max_ids[mailbox_name]))
        f_uid.write('\n')

        # get messages
        messages = engine.execute(
            "  select * from dbmail_physmessage phy, dbmail_messages msg "
            "   where     msg.physmessage_id = phy.id "
            "         and mailbox_idnr = %s "
            "order by msg.message_idnr", mailbox['mailbox_idnr']) # the dovecot-uidlist file needs to be ordered.

        mail_file = ""

        # go through and create files for each
        mailbox_size = 0
        for message in messages:
            totalmessages += 1
            sys.stdout.flush()

            # get message contents
            # This assumes that the messageblks are put together sequentially by messageblk_idnr.
            # This may be a bad assumption
            contents = engine.execute(
                "select * from dbmail_messageblks blks, dbmail_messages msg where 1=1"
                "and msg.physmessage_id = blks.physmessage_id "
                "and message_idnr = %s "
                "and deleted_flag = 0"
                "order by messageblk_idnr ASC", message['message_idnr']
            )

            # create filename
            t = mktime(message.internal_date.timetuple())
            filename = message['unique_id'] + ":2,"

            # look at some flags, this could be extended
            if (message['answered_flag'] == 1):
                filename += "R"

            if (message['seen_flag'] == 1):
                filename += "S"

            if (message['flagged_flag'] == 1):
                filename += "F"

            if (message['draft_flag'] == 1):
                filename += "D"

            mail_file = mailbox_dir + "/cur/" + filename

            f = open(mail_file, 'w')
            message_size = 0
            for c in contents:
                f.write(str(c.messageblk))
                message_size += len(c.messageblk)

            mailbox_size += message_size
            user_size += message_size
            global_size += message_size

            f.close()

            os.utime(mail_file, (time(), t))

            f_uid.write(str(message.message_idnr))
            f_uid.write(" ")
            f_uid.write(filename.split(":")[0])
            f_uid.write("\n")

            print "\t",
            print '\033[91m' + ('%-'+str(maxlen)+'s') % mailbox.name + '\033[0m', 
            print '%5d / %5d' % (totalmessages, messages.rowcount), 
            print "\033[93m%13s\033[0m bytes" % thous(message_size), 
            print os.path.basename(mail_file), 
            print "\r",

        print "\t",
        print '\033[92m' + ('%-'+str(maxlen)+'s') % mailbox.name + '\033[0m',
        print '%5d' % totalmessages, '/', '%5d' % messages.rowcount,
        print "\033[93m%13s\033[0m bytes total." % thous(mailbox_size),
        print " " * len(os.path.basename(mail_file))

        f_uid.close()

    print '\t', thous(user_size), "bytes total.\n"

    f = open(MAILDIR + "subscriptions", "w")
    for s in subs:
        f.write(s)
        f.write('\n')
    f.close()

print "Done. %s bytes in total.\n" % thous(global_size)
