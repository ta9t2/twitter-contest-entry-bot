#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This bot is for automatically to destroy your all friendships.

import tweepy
from datetime import datetime
import csv
import time
import json
import sys
import os


def get_api(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)
    return api


def log(level, text):
    timemes = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
    levmes = '[ERROR]' if level == 'e' else '[INFO]'
    logmes = ''.join(str(text).splitlines())
    print(logmes)
    with open('bot.log', mode='a', encoding="utf-8_sig") as f:
        f.write(timemes + levmes + logmes + '\n')


def unfollow_friend(api, friend_user_id):
    result_destroy = dict()
    screen_name = ''
    name = ''
    try:
        api.destroy_friendship(friend_user_id)
        screen_name = api.get_user(friend_user_id).screen_name
        name = api.get_user(friend_user_id).name
        result_destroy = dict(user_id=friend_user_id, screen_name=screen_name,
                              name=name, is_destroy=True, comment='Successfully unfollowed')
    except tweepy.error.TweepError as e:
        result_destroy = dict(user_id=friend_user_id, screen_name=screen_name,
                              name=name, is_destroy=False, comment=e.reason)
    return result_destroy


def print_progress(index, result):
    mes = list()
    mes += ['---------- [{m1}] ----------------------------------------'.format(
        m1=(index + 1))]
    mes += ['unfollow: {m1}(@{m2}) -> {m3}'.format(m1=result['name'],
                                                    m2=result['screen_name'], m3=result['comment'])]
    for m in mes:
        log('i', m)


def convert_result_dic_to_list(result):
    row = list()
    row += [result['user_id']]
    row += [result['screen_name']]
    row += [result['name']]
    row += [result['is_destroy']]
    row += [result['comment']]
    return row


def write_results(results, filename):
    header = [[
        'unfollow-user_id',
        'unfollow-screen_name',
        'unfollow-name',
        'unfollow-is_unfollowed',
        'unfollow-comment',
    ]]

    rows = list()
    for result in results:
        rows.append(convert_result_dic_to_list(result))

    with open(filename, mode='w', encoding="utf-8_sig") as f:
        writer = csv.writer(f, delimiter=',', quotechar='"',
                            lineterminator='\n', quoting=csv.QUOTE_ALL)
        writer.writerows(header + rows)


def is_yes():
    yes = ['yes', 'y', 'ye']
    no = ['no', 'n']
    while True:
        choice = input("Please respond with 'yes' or 'no': ").lower().strip()
        if choice in yes:
            return True
        elif choice in no:
            return False


if __name__ == '__main__':
    log('i', 'START {script_name}'.format(
        script_name=os.path.basename(__file__)))

    destroy_list = list()
    results = list()
    start_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = 'result_DestroyAllFriendshipsBot_' + start_time + '.csv'

    # Load configurations from the JSON file.
    with open('config.json', mode='r', encoding="utf-8_sig") as f:
        cf = json.load(f)
    CONSUMER_KEY = cf['consumer_key']
    CONSUMER_SECRET = cf['consumer_secret']
    ACCESS_TOKEN = cf['access_token']
    ACCESS_TOKEN_SECRET = cf['access_token_secret']
    INTERVAL_TIME = cf['interval_time']

    # Initialize the API
    api = get_api(CONSUMER_KEY, CONSUMER_SECRET,
                  ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # Count of my friends
    friends_before = len(api.friends_ids(api.me().screen_name))

    # Confirm if you want to continue
    confirmation_message = 'Continuing will be unfollowed all your friends on Twitter. To complete will take {complete_time} secs(={friend_cnt} friends * {interval_time} secs interval time). Are you sure you want to continue?'.format(
        complete_time=(friends_before * INTERVAL_TIME), friend_cnt=friends_before, interval_time=INTERVAL_TIME)
    log('i', confirmation_message)
    if not is_yes():
        log('i', 'STOP {script_name}'.format(
            script_name=os.path.basename(__file__)))
        sys.exit()
    log('i', 'CONTINUE {script_name}'.format(
        script_name=os.path.basename(__file__)))

    # Destroy friendship
    destroy_list = api.friends_ids(api.me().screen_name)
    for index, friend in enumerate(destroy_list):
        # Unfollow
        friend_user_id = friend
        result = unfollow_friend(api, friend_user_id)
        results.append(result)

        # Print progress
        print_progress(index, result)

        # Wait a few minutes to keep not to ban my account
        if result['is_destroy']:
            log('i', 'time.sleep(' + str(INTERVAL_TIME) + ')')
            time.sleep(INTERVAL_TIME)

    # Write out the results on a CSV sheet
    write_results(results, output_filename)
    log('i', 'DONE! See the "' + output_filename + '" file.')

    # Count of my friends
    friends_after = len(api.friends_ids(api.me().screen_name))
    log('i', 'Friends: ' +
        str(friends_before) + ' -> ' + str(friends_after))
