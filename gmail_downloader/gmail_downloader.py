#!/usr/bin/python

import optparse
import email
import getpass
import os
import string
import datetime

import imaplib

def get_options():
    """Parse the command line options. Use -h to see the option"""
    parser = optparse.OptionParser(description='Download messages from an IMAP server (like GMail) and create one file per message.')
    
    parser.add_option('--username', '-u', type='string', default='', dest='username', help='GMail account name to be downloaded')
    parser.add_option('--password', '-p', type='string', default='', dest='password', help='Password for GMail account specified')
    parser.add_option('--start-pos', '-s', type='int', default=0, dest='start_index', help='Message position to start downloading at.')
    parser.add_option('--save-dir', type='string', default='/tmp/', dest='save_dir', help='Directory where messages should be saved.')
    parser.add_option('--mailbox', type='string', default='INBOX', dest='mailbox', help='Remote IMAP mailbox to download')
    parser.add_option('--since', type='string', default='2011-Jan-01 00:00:00', dest='since', help='Download all messages after this data.')
    parser.add_option('--verbose', '-v', action='store_true', default=False, dest='verbose', help='Write debug strings to standard out.')
    
    return parser.parse_args()

def get_mailboxes(imap_lib):
    """Return a list of all of the mailboxes in the given option imap server"""
    mailbox_names = []
    
    result, mailboxes = imap_lib.list()
    if result == 'OK':
        print 'Total Mailboxes: ' + str(len(mailboxes))
        
        for mailbox in mailboxes:
            print mailbox
            mailbox_name = mailbox.split(' "/" ')[1].strip('"')
            mailbox_names.append(mailbox_name)
    else:
        print 'ERROR: Failed to receive mailboxes from account.'
            
    return mailbox_names


def message_to_file(path, message):
    """Write a given email message to the given file path"""
    f = open(path, 'w+')
    f.write(message.as_string())
    f.close()
    
def debug_out(options, message):
    if options.verbose:
        t = datetime.datetime.now()
        full_message = "%s IMAP DOWNLOADER: %s" % (t.isoformat(), message) 
        print full_message
    

def main():
    """This program will download messages from the GMail IMAP server and place each message
    into its own files. The name of the file is the unique ID of the message.
    """
    (options, args) = get_options()
    debug_out(options, "Options: %s" % options)

    username = options.username
    if username == '':    
        username = raw_input('Enter gmail account you want to download: ')
        
    password = options.password
    if password == '':
        password = getpass.getpass('Enter your gmail password:')
    
    imap_lib = imaplib.IMAP4_SSL('imap.gmail.com')
    imap_lib.login(username, password)
    
    mailbox = options.mailbox
        
    result, msg_count = imap_lib.select(mailbox)
    debug_out(options, 'Select command returned result of %s with %s messages' % (result, msg_count))
    if not result == 'OK':
        raise Exception, 'IMAP fetch returned: ' + result
           
    # Get all messages after last run.
    search_param = '(SINCE %s)' % (options.since)
    result, search_results = imap_lib.search(None, search_param)
    all_message_ids = string.split(search_results[0]);
    msg_count = len(all_message_ids)
    debug_out(options, 'Folder %s has %d new messages since %s.' % (mailbox, msg_count, options.since))

    for message_id in all_message_ids:

        result, message_list = imap_lib.fetch(message_id, '(RFC822)')

        if not result == 'OK':
            raise Exception, 'IMAP fetch returned: ' + result

        message = message_list[0]
            
        if len(message) > 1:
            
            parsed_message = email.Parser.Parser().parsestr(message[1])
            file_name = parsed_message.get('Message-ID')

            if file_name is None or len(file_name) < 1:
                debug_out(options,'ERROR: Message %d has no Message-ID' % (index))
            else:    
                clean_file_name = file_name.strip('<>') + '.eml'
                clean_file_name = string.replace(clean_file_name, '/', '_')
                path = '%s/%s' % (options.save_dir, clean_file_name)
                
                if not os.path.exists(path):
                    message_to_file(path, parsed_message)
                    debug_out(options, 'Wrote message %s to %s' % (message_id, path))
                else:
                    debug_out(options, 'NO MESSAGE WRITTEN. Message %s already exists at %s' % (message_id, path))
            
                    
if __name__ == "__main__":
    main()
