#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This bot is for automatically to destroy your friendships from old friends to specified number.

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


def unfollow_friend(api, friend_user_id, ignore_user_ids):
    result_destroy = dict()
    screen_name = ''
    name = ''

    # If including ignore user, not to destroy
    is_ignore, ignore_user_id, ignore_screen_name, ignore_name = check_ignore(
        [friend_user_id], ignore_user_ids)
    if is_ignore:
        comment = 'Ignored'
        result_destroy = dict(user_id=ignore_user_id, screen_name=ignore_screen_name,
                              name=ignore_name, is_destroy=False, comment=comment)
        return result_destroy

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


def convert_ignore_users_to_ignore_user_ids(ignore_users):
    result_ignore_user_ids = list()
    for user in ignore_users:
        try:
            result_ignore_user_ids.append(api.get_user(user).id)
        except tweepy.error.TweepError as e:
            log('e', 'func=' + str(sys._getframe().f_code.co_name) + ', user="' +
                str(user) + '", e.reason=' + str(e.reason))
    return result_ignore_user_ids


def check_ignore(user_ids, ignore_user_ids):
    is_ignore = False
    ignore_user_id = ''
    ignore_screen_name = ''
    ignore_name = ''
    for user_id in user_ids:
        if user_id in ignore_user_ids:
            is_ignore = True
            ignore_user_id = user_id
            try:
                ignore_screen_name = api.get_user(user_id).screen_name
                ignore_name = api.get_user(user_id).name
            except tweepy.error.TweepError as e:
                log('e', 'func=' + str(sys._getframe().f_code.co_name) + ', is_ignore="' + str(is_ignore) + ', ignore_user_id="' + str(ignore_user_id) +
                    ', ignore_screen_name="' + str(ignore_screen_name) + ', ignore_name="' + str(ignore_name) + '", e.reason=' + str(e.reason))
    return is_ignore, ignore_user_id, ignore_screen_name, ignore_name


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


def update_destroy_list(destroy_list_scr, results, filename):
    destroy_list = destroy_list_scr
    for result in results:
        if result['is_destroy']:
            for index, destroy_friend in enumerate(destroy_list_scr):
                if result['user_id'] == destroy_friend[1]:
                    del destroy_list[index]

    with open(filename, mode='w', encoding="utf-8_sig") as f:
        writer = csv.writer(f, delimiter=',', quotechar='"',
                            lineterminator='\n', quoting=csv.QUOTE_ALL)
        writer.writerows(destroy_list)


if __name__ == '__main__':
    log('i', 'START {script_name}'.format(
        script_name=os.path.basename(__file__)))

    destroy_list = list()
    results = list()
    start_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = 'result_UnfollowBot_' + start_time + '.csv'

    # Load configurations from the JSON file.
    with open('config.json', mode='r', encoding="utf-8_sig") as f:
        cf = json.load(f)
    CONSUMER_KEY = cf['consumer_key']
    CONSUMER_SECRET = cf['consumer_secret']
    ACCESS_TOKEN = cf['access_token']
    ACCESS_TOKEN_SECRET = cf['access_token_secret']
    INTERVAL_TIME = cf['interval_time']
    DESTROY_LIST_FILENAME = cf['destroy_friendship']['destroy_list_filename']
    DESTROY_COUNT = cf['destroy_friendship']['destroy_count']
    IGNORE_USERS = cf['destroy_friendship']['ignore_users']

    # Load unfollow-list
    with open(DESTROY_LIST_FILENAME, mode='r', encoding="utf-8_sig") as f:
        reader = csv.reader(f)
        destroy_list = [row for row in reader]

    # Initialize the API
    api = get_api(CONSUMER_KEY, CONSUMER_SECRET,
                  ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # Count of my friends
    friends_before = len(api.friends_ids(api.me().screen_name))

    # Create ignore user id list
    ignore_user_ids = convert_ignore_users_to_ignore_user_ids(IGNORE_USERS)

    # Destroy friendship
    for index, friend in enumerate(destroy_list):
        if index >= DESTROY_COUNT:
            break

        # Unfollow
        friend_user_id = friend[1]
        result = unfollow_friend(api, friend_user_id, ignore_user_ids)
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

    # Update destroy list
    update_destroy_list(destroy_list, results, DESTROY_LIST_FILENAME)
    log('i', 'Updated destroy list: ' + DESTROY_LIST_FILENAME)
