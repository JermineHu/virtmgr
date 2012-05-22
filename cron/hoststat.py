#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# getinfo - Script get info on snmp
#			on switch EDGE-CORE
#			
# Copyright © 2010 - X-systems
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# Authors:
# Anatoliy Guskov <anatoliy.guskov@gmail.com>

import MySQLdb
import smtplib
import socket
import re
from time import strftime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
	conn = MySQLdb.connect (host = "localhost",
    	                    user = "root",
        	                passwd = "root",
            	            db = "virtmgr")
except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

cursor = conn.cursor()
cursor.execute("SELECT id, ipaddr, state, user_id FROM model_host")
rows = cursor.fetchall()

for row in rows:
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(1)
		s.connect((row[1], 16509))
		s.close()
		status = 1
		if row[2] == 2:
			cursor.execute("UPDATE model_host SET state=%s WHERE id=%s", (status, row[0]))
			datetime = strftime("%y-%m-%d %H:%M:%S")
			cursor.execute("INSERT INTO model_log (host_id, type, message, date, user_id) VALUE (%s, 'scheduler', 'The server is available', %s, %s)", (row[0], datetime, row[3]))
		else:
			cursor.execute("UPDATE model_host SET state=%s WHERE id=%s", (status, row[0]))
	except:
		status = 2
		if row[2] == 1:
			cursor.execute("UPDATE model_host SET state=%s WHERE id=%s", (status, row[0]))
			datetime = strftime("%y-%m-%d %H:%M:%S")
			cursor.execute("INSERT INTO model_log (host_id, type, message, date, user_id) VALUE (%s, 'scheduler', 'The server is not available', %s, %s)", (row[0], datetime, row[3]))

cursor.close()
conn.commit()
conn.close()