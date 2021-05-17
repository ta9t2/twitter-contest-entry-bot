#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Twitter Bot Common Functions

import datetime
import inspect
import json
import logging
import os
import smtplib
import sys
from email.mime.text import MIMEText
from email.utils import formatdate

from requests_oauthlib import OAuth1Session


import tweepy


CONTD = 'Continued'
ABORT = 'Abnormal end'


def log_init():
    # Define log format
    formatter = '[%(asctime)s][%(levelname)s]%(message)s'

    # Get caller's module name & Define log file name
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    callermodulename = os.path.basename(module.__file__)
    filename = 'log/{logname}.log'.format(logname=callermodulename)

    # Define log conf
    logging.basicConfig(level=logging.INFO,
                        format=formatter, filename=filename)
    return


def log(level, mes='', func='', hdlg=CONTD):
    # level='e':error, 'i' or others:info

    # text = '{mes}, func={func}, hdlg={hdlg}'.format(mes=mes, func=func, hdlg=hdlg)
    text = '{mes}'.format(mes=mes)
    if not func == '':
        text += ', func={func}'.format(func=func)
    if not hdlg == CONTD:
        text += ', hdlg={hdlg}'.format(hdlg=hdlg)

    # Print log
    print(text)

    # Write log
    if level == 'e':
        logging.error(text)
    else:
        logging.info(text)

    # Exit status
    if hdlg == ABORT:
        os._exit(1)

    return


def load_config(filename='config/config.json'):
    # Load configurations
    config = dict()
    try:
        with open(filename, mode='r', encoding='utf-8_sig') as f:
            config = json.load(f)
    except Exception as e:
        log('e', mes=e, func=str(sys._getframe().f_code.co_name), hdlg=ABORT)
    return config


def get_api(consumer_key, consumer_secret, access_token, access_token_secret):
    try:
        api = OAuth1Session(consumer_key, consumer_secret,
                            access_token, access_token_secret)
    except Exception as e:
        log('e', mes=e, func=str(sys._getframe().f_code.co_name), hdlg=ABORT)
    return api


def get_direct_messages(api, count):
    endpoint = 'https://api.twitter.com/1.1/direct_messages/events/list.json'
    params = {'count': count}
    dms = dict()
    try:
        res = api.get(endpoint, params=params)
        dms = json.loads(res.text)
    except Exception as e:
        log('e', mes=e, func=str(sys._getframe().f_code.co_name), hdlg=ABORT)
    return dms


def get_userinfo_from_user_id(api, user_id):
    userinfo = dict()
    endpoint = 'https://api.twitter.com/1.1/users/show.json'
    params = {'user_id': user_id}
    userinfo = dict()
    try:
        res = api.get(endpoint, params=params)
        dic = json.loads(res.text)
        userinfo = {
            'user_id': user_id,
            'name': dic['name'],
            'screen_name': dic['screen_name']
        }
    except Exception as e:
        log('e', mes=e, func=str(sys._getframe().f_code.co_name), hdlg=CONTD)
        userinfo = {
            'user_id': user_id,
            'name': 'N/A',
            'screen_name': 'N/A'
        }
    return userinfo


def get_myinfo(api):
    userinfo = dict()
    endpoint = 'https://api.twitter.com/1.1/account/verify_credentials.json'
    params = {}
    userinfo = dict()
    try:
        res = api.get(endpoint, params=params)
        dic = json.loads(res.text)
        userinfo = {
            'user_id': dic['id_str'],
            'name': dic['name'],
            'screen_name': dic['screen_name']
        }
    except Exception as e:
        log('e', mes=e, func=str(sys._getframe().f_code.co_name), hdlg=CONTD)
        userinfo = {
            'user_id': 'N/A',
            'name': 'N/A',
            'screen_name': 'N/A'
        }
    return userinfo


def mail(subject, body, to_addr, gmail_addr, gmail_pw):
    try:
        # Create mail
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = gmail_addr
        msg['To'] = to_addr
        msg['Date'] = formatdate()

        # Send mail
        smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpobj.ehlo()
        smtpobj.starttls()
        smtpobj.ehlo()
        smtpobj.login(gmail_addr, gmail_pw)
        smtpobj.sendmail(gmail_addr, to_addr, msg.as_string())
        smtpobj.close()
    except Exception as e:
        log('e', mes=e, func=str(sys._getframe().f_code.co_name), hdlg=ABORT)
    return


def get_timenow():
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')


def get_tweet_url(screen_name, tweet_id):
    tweet_url = 'https://twitter.com/{screen_name}/status/{tweet_id}'.format(
        screen_name=screen_name, tweet_id=tweet_id)
    return tweet_url


def get_userstr(user_id, screen_name, name):
    userstr = '{name}(@{screen_name}/{user_id})'.format(user_id=user_id,
                                                        screen_name=screen_name, name=name)
    return userstr


def is_ignore(user_ids, ignore_user_ids):
    for user_id in user_ids:
        if user_id in ignore_user_ids:
            log('i', mes='user_id={id} is in the ignore list.'.format(
                id=user_id), func=str(sys._getframe().f_code.co_name), hdlg=CONTD)
            return True
    return False


def is_yes():
    yes = ['yes', 'y', 'ye']
    no = ['no', 'n']
    while True:
        choice = input("Please respond with 'yes' or 'no': ").lower().strip()
        if choice in yes:
            return True
        elif choice in no:
            return False


def twp_get_api(consumer_key, consumer_secret, access_token, access_token_secret):
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True,
                         wait_on_rate_limit_notify=True)
    except Exception as e:
        log('e', mes=e, func=str(sys._getframe().f_code.co_name), hdlg=ABORT)
    return api


def twp_convert_screen_names_to_user_ids(api, screen_names):
    user_ids = list()
    for screen_name in screen_names:
        try:
            user_ids.append(api.get_user(screen_name).id)
        except tweepy.error.TweepError as e:
            log('e', mes=e, func=str(sys._getframe().f_code.co_name), hdlg=CONTD)
    return user_ids


def twp_follow_user_id(api, user_id):
    # Follow(Create friendship with a new user)
    result_follow = dict()
    screen_name = ''
    name = ''
    try:
        friendship = api.show_friendship(
            source_id=api.me().id, target_id=user_id)
        screen_name = api.get_user(user_id).screen_name
        name = api.get_user(user_id).name

        if friendship[0].following:
            result_follow = dict(user_id=user_id, screen_name=screen_name,
                                 name=name, is_followed=False, comment='Already followed')
        else:
            api.create_friendship(user_id)
            result_follow = dict(user_id=user_id, screen_name=screen_name,
                                 name=name, is_followed=True, comment='Successfully followed')
    except tweepy.error.TweepError as e:
        result_follow = dict(user_id=user_id, screen_name=screen_name,
                             name=name, is_followed=False, comment=e.reason)
    return result_follow


def twp_follow_user_ids(api, user_ids):
    # Follow(Create friendship with new users)
    result_follows = list()
    for user_id in user_ids:
        result_follows.append(twp_follow_user_id(api, user_id))
    return result_follows


def twp_retweet_tweet_id(api, tweet_id):
    # Retweet
    result_retweet = dict()
    try:
        api.retweet(tweet_id)
        result_retweet = dict(
            tweet_id=tweet_id, is_retweeted=True, comment='Successfully retweeted')
    except tweepy.error.TweepError as e:
        result_retweet = dict(
            tweet_id=tweet_id, is_retweeted=False, comment=e.reason)
    return result_retweet


def twp_unfollow_user_id(api, user_id):
    # Destory friendship with a user
    result_destroy = dict()
    screen_name = ''
    name = ''
    try:
        api.destroy_friendship(user_id)
        screen_name = api.get_user(user_id).screen_name
        name = api.get_user(user_id).name
        result_destroy = dict(user_id=user_id, screen_name=screen_name,
                              name=name, is_destroyed=True, comment='Successfully unfollowed')
    except tweepy.error.TweepError as e:
        result_destroy = dict(user_id=user_id, screen_name=screen_name,
                              name=name, is_destroyed=False, comment=e.reason)
    return result_destroy


def twp_unfollow_user_ids(api, user_ids):
    # Destory friendship
    result_destroys = list()
    for user_id in user_ids:
        result_destroys.append(twp_unfollow_user_id(api, user_id))
    return result_destroys


def dict_to_str(dicdata):
    return json.dumps(dicdata)
