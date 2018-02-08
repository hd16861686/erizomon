#!/usr/bin/python
import sys
import json
import smtplib
from email.mime.text import MIMEText
from elasticsearch import Elasticsearch, helpers

def get_config_path( argv ):
    if len( argv ) is 0:
        return "./config/config.json"
    else:
        return argv[0]

def get_config( path ):
    try:
        cfile = open( path, 'r' )
        config = json.load( cfile )
        cfile.close()
        return config
    except IOError:
        sys.exit( "Cannot open configuration file: {0}".format( path ) )

def get_log_scanner( config ):
    es = Elasticsearch( config['elasticsearch'] )
    res = helpers.scan( client = es, scroll = "2m", query = config['query'], index = config["index"] )
    return res

def main( argv ):
    config = get_config( get_config_path( argv ) )
    alert = False
    errmsg = list()
    errtime = None
    for hit in get_log_scanner( config ):
        if "ErizoController" in hit['fields']['message'][0]:
            alert = True
            errmsg.append( hit['fields']['message'][0] )
            errtime = hit['fields']['@timestamp'][0]
    if alert:
        mailer = smtplib.SMTP( config['smtphost'] )
        msg = MIMEText( config['msgtext'].format( errtime, "\n".join( errmsg[-10:] ) ) )
        msg['Subject'] = config['msgsubject']
        msg['From'] = config['sender']
        msg['To'] = ", ".join( config['recipients'] )
        mailer.sendmail( config['sender'], config['recipients'], msg.as_string() )
        #print msgtext

if __name__ == "__main__":
    main(sys.argv[1:])
