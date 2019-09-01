#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This bot is for automatically to destroy your all friendships.

import os
import time

import tweepy

import tb_common as tbc
import tb_unfollow


if __name__ == '__main__':
    tbc.log_init()
    tbc.log('i', mes='START SCRIPT')

    # Load configurations from the JSON file.
    CONFIG = tbc.load_config()

    # Set result file name
    result_filename = '{result_dir}/destroy_all_friendship_{datetime}.csv'.format(
        result_dir=CONFIG['result_dir'], datetime=tbc.get_timenow())

    # Initialize the API
    api = tbc.twp_get_api(CONFIG['consumer_key'], CONFIG['consumer_secret'],
                          CONFIG['access_token'], CONFIG['access_token_secret'])

    # Count of my friends
    friends_before = len(api.friends_ids(api.me().screen_name))

    # Confirm if you want to continue
    mes = 'Continuing will be unfollowed all of your friends on Twitter. To complete will take {complete_time} secs(={friend_cnt} friends * {interval_time} secs interval time). Are you sure you want to continue?'.format(
        complete_time=(friends_before * CONFIG['interval_time']), friend_cnt=friends_before, interval_time=CONFIG['interval_time'])
    tbc.log('i', mes=mes)
    if not tbc.is_yes():
        tbc.log('i', mes='Stop to destroy your friendship.')
        os._exit(1)
    tbc.log('i', mes='Destroy your friendship between you and all.')

    # Destroy friendship
    destroy_list = api.friends_ids(api.me().screen_name)
    for index, user_id in enumerate(destroy_list):
        result = dict()

        # Unfollow
        result['unfollows'] = tbc.twp_unfollow_user_ids(
            api, [user_id])

        # Print progress
        tb_unfollow.print_progress(index, result)

        # Write result
        tb_unfollow.write_result(result, result_filename)

        # Wait a few minutes to keep not to ban my account
        for unfollow in result['unfollows']:
            if unfollow['is_destroyed']:
                tbc.log('i', mes='Waiting: time.sleep({it})'.format(
                    it=CONFIG['interval_time']))
                time.sleep(CONFIG['interval_time'])
                break

    # Print & Count of my friends
    friends_after = len(api.friends_ids(api.me().screen_name))
    tbc.log(
        'i', mes='Friends: {fb} -> {fa}'.format(fb=friends_before, fa=friends_after))

    tbc.log('i', mes='DONE')
