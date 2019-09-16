#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This bot is for automatically to destroy your friendships from old friends to specified number.

import csv
import sys
import time

import tweepy

import tb_common as tbc


def print_progress(index, result):
    mess = list()
    mess += ['---------- [{m1}] ----------------------------------------'.format(
        m1=(index + 1))]
    userstr = tbc.get_userstr(user_id=result['unfollow']['user_id'],
                              screen_name=result['unfollow']['screen_name'], name=result['unfollow']['name'])
    mess += ['unfollow: {m1} -> {m2}'.format(
        m1=userstr, m2=result['unfollow']['comment'])]
    for mes in mess:
        tbc.log('i', mes=mes)
    return


def write_updated_friend_list(unfollow, filename):
    # Load friend list
    friends = list()
    try:
        with open(filename, mode='r', encoding='utf-8_sig') as f:
            reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_ALL)
            for row in reader:
                friend = dict()
                friend['user_id'] = int(row[0])
                friend['screen_name'] = row[1]
                friend['name'] = row[2]
                friends.append(friend)
    except Exception as e:
        tbc.log('e', mes=e, func=str(
            sys._getframe().f_code.co_name), hdlg=tbc.ABORT)

    # Remove destroy friends from friend list
    updated_friendlist = list()
    for friend in friends:
        if friend['user_id'] != unfollow['user_id']:
            updated_friendlist.append(friend)

    # Update friend list
    # user_id, screen_name, name
    with open(filename, mode='w', encoding="utf-8_sig") as f:
        writer = csv.writer(f, delimiter=',', quotechar='"',
                            lineterminator='\n', quoting=csv.QUOTE_ALL)
        for friend in updated_friendlist:
            writer.writerow(
                [friend['user_id'], friend['screen_name'], friend['name']])
    return


def write_result(result, filename):
    # userstr, is_unfollowed, comment
    with open(filename, mode='a', encoding="utf-8_sig") as f:
        writer = csv.writer(f, delimiter=',', quotechar='"',
                            lineterminator='\n', quoting=csv.QUOTE_ALL)
        row = list()
        row += [tbc.get_userstr(result['unfollow']['user_id'],
                                result['unfollow']['screen_name'], result['unfollow']['name'])]
        row += [result['unfollow']['is_destroyed']]
        row += [result['unfollow']['comment']]
        writer.writerow(row)
    return


if __name__ == '__main__':
    tbc.log_init()
    tbc.log('i', mes='START SCRIPT')

    # Load configurations from the JSON file.
    CONFIG = tbc.load_config()

    # Set result file name
    result_filename = '{result_dir}/unfollow_{datetime}.csv'.format(
        result_dir=CONFIG['result_dir'], datetime=tbc.get_timenow())

    # Load friend list
    friends = list()
    try:
        with open(CONFIG['destroy_friendship']['destroy_list_filename'], mode='r', encoding='utf-8_sig') as f:
            reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_ALL)
            for row in reader:
                friend = dict()
                friend['user_id'] = int(row[0])
                friend['screen_name'] = row[1]
                friend['name'] = row[2]
                friends.append(friend)
    except Exception as e:
        tbc.log('e', mes=e, func=str(
            sys._getframe().f_code.co_name), hdlg=tbc.ABORT)

    # Initialize the API
    api = tbc.twp_get_api(CONFIG['consumer_key'], CONFIG['consumer_secret'],
                          CONFIG['access_token'], CONFIG['access_token_secret'])

    # Count of my friends
    friends_before = len(api.friends_ids(api.me().screen_name))

    # Get ignore users and Convert screen_name to user_id
    ignore_user_ids = tbc.twp_convert_screen_names_to_user_ids(
        api, CONFIG['destroy_friendship']['ignore_users'])

    # Destroy friendship
    for index, friend in enumerate(friends):
        result = dict()
        if index >= CONFIG['destroy_friendship']['destroy_count']:
            break

        # whether or not a icluding ignore list
        if tbc.is_ignore([friend['user_id']], ignore_user_ids):
            tbc.log('i', mes='Skipped, for the user is a ignore user: user_id={user_id}, screen_name={screen_name}, name={name}'.format(
                user_id=friend['user_id'], screen_name=friend['screen_name'], name=friend['name']))
            continue

        # Unfollow
        result['unfollow'] = tbc.twp_unfollow_user_id(
            api, friend['user_id'])

        # Print progress
        print_progress(index, result)

        # Update(Remove lines) destroy friend list
        write_updated_friend_list(
            result['unfollow'], CONFIG['destroy_friendship']['destroy_list_filename'])

        # Write result
        write_result(result, result_filename)

        # Wait a few minutes to keep not to ban my account
        if result['unfollow']['is_destroyed']:
            tbc.log('i', mes='Waiting: time.sleep({it})'.format(
                it=CONFIG['interval_time']))
            time.sleep(CONFIG['interval_time'])

    # Print & Count of my friends
    friends_after = len(api.friends_ids(api.me().screen_name))
    tbc.log(
        'i', mes='Friends: {fb} -> {fa}'.format(fb=friends_before, fa=friends_after))

    tbc.log('i', mes='DONE')
