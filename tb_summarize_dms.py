#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This bot is for automatically to summarize DMs on Twitter to send the summary by email.

import datetime
import sys
import time

import tb_common as tbc


def summarize_direct_messages(api, direct_messages, last_timestamp, timezone):
    sum_dms = list()
    if len(direct_messages) != 0:
        # Summaraize DMs from the latest timestamp to the last timestamp
        for direct_message in direct_messages['events']:
            if direct_message['created_timestamp'] <= last_timestamp:
                break
            timestamp = (str)(datetime.datetime.fromtimestamp((int)(
                direct_message['created_timestamp'][0:10]), datetime.timezone(datetime.timedelta(hours=timezone))))
            user_info = tbc.get_userinfo_from_user_id(
                api, direct_message['message_create']['sender_id'])
            sum_dm = {
                'dm_id': direct_message['id'],
                'timestamp': timestamp,
                'sender_info': user_info['name'] + '(@' + user_info['screen_name'] + ')',
                'text': direct_message['message_create']['message_data']['text']
            }
            sum_dms.append(sum_dm)

            # Wait a few minutes to keep not to ban my account
            tbc.log('i', mes='Waiting: time.sleep({it})'.format(
                it=CONFIG['interval_time']))
            time.sleep(CONFIG['interval_time'])

    return sum_dms


def create_message(api, sum_dms):
    # Get my screen_name
    my_screen_name = tbc.get_myinfo(api)['screen_name']

    # Make mail subject
    subject = '[bot] Twitter DM: @' + my_screen_name

    # Make mail body
    body = ''
    border = '--------------------' + '\n'
    body += '@' + my_screen_name + "'s direct messages are as follows:" + '\n'
    body += border
    if len(sum_dms) == 0:
        body += 'N/A' + '\n'
        body += border
    else:
        for sum_dm in sum_dms:
            body += 'dmid: ' + sum_dm['dm_id'] + '\n'
            body += 'timestamp: ' + sum_dm['timestamp'] + '\n'
            body += 'sender: ' + sum_dm['sender_info'] + '\n'
            body += 'text: ' + sum_dm['text'] + '\n'
            body += border

    return subject, body


def get_latest_timestamp(direct_messages):
    timestamp = ''
    if len(direct_messages) != 0:
        if len(direct_messages['events']) != 0:
            timestamp = direct_messages['events'][0]['created_timestamp']
    return timestamp


if __name__ == '__main__':
    tbc.log_init()
    tbc.log('i', mes='START SCRIPT')

    # Load configurations
    CONFIG = tbc.load_config()
    SUM_LAST_TIMESTAMP = ''
    try:
        with open(CONFIG['sum']['last_timestamp_filename'], mode='r', encoding='utf-8_sig') as f:
            SUM_LAST_TIMESTAMP = f.readline().strip()
    except Exception as e:
        tbc.log('e', mes=e, func=str(
            sys._getframe().f_code.co_name), hdlg=tbc.CONTD)

    # Set result file name
    result_filename = '{result_dir}/sumdms_{datetime}.txt'.format(
        result_dir=CONFIG['result_dir'], datetime=tbc.get_timenow())

    # Initialize API
    api = tbc.get_api(CONFIG['consumer_key'], CONFIG['consumer_secret'],
                      CONFIG['access_token'], CONFIG['access_token_secret'])

    # Get DMs
    dms = tbc.get_direct_messages(api, CONFIG['sum']['count'])

    # Summaraize DMs
    sum_dms = summarize_direct_messages(
        api, dms, SUM_LAST_TIMESTAMP, CONFIG['timezone'])
    for sum_dm in sum_dms:
        tbc.log('i', mes='Summarized DMs: sum_dm=' + str(sum_dm))

    # Send mail
    subject, body = create_message(api, sum_dms)
    tbc.mail(subject, body, CONFIG['sum']['mailto'],
             CONFIG['sum']['gmail_addr'], CONFIG['sum']['gmail_pw'])
    tbc.log('i', mes='Mailed: mailto={mailto}, gmail={gmail}'.format(
        mailto=CONFIG['sum']['mailto'], gmail=CONFIG['sum']['gmail_addr']))

    # Update latest timestamp
    latest_timestamp = get_latest_timestamp(dms)
    with open(CONFIG['sum']['last_timestamp_filename'], mode='w', encoding='utf-8_sig') as f:
        f.write(latest_timestamp)
    tbc.log('i', mes='Updated timestamp: latest_timestamp={latest_timestamp}, filename={fn}'.format(
        latest_timestamp=latest_timestamp, fn=CONFIG['sum']['last_timestamp_filename']))

    # Write result
    result = ''
    result += 'latest_timestamp: {lt}\n'.format(lt=latest_timestamp)
    result += 'mail_subject: {ms}\n'.format(ms=subject)
    result += 'mail_body: {mb}\n'.format(mb=body)
    with open(result_filename, mode='w', encoding='utf-8_sig') as f:
        f.write(result)
    tbc.log('i', mes='Wrote the result: filename={fn}'.format(
        fn=result_filename))

    tbc.log('i', mes='DONE')
