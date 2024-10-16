from config import TTV_CLIENT_ID, TTV_CLIENT_SECRET, TTV_USERNAME
from audio.generate_username_audio import generate_username_audio
from audio.combine_audio import combine_audio

from twitchAPI.twitch import Twitch
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.object.eventsub import ChannelFollowEvent, ChannelSubscribeEvent, ChannelSubscriptionGiftEvent, ChannelSubscriptionMessageEvent
from twitchAPI.type import AuthScope
from twitchAPI.helper import first
import requests
import logging

import os
import sys

TARGET_SCOPE = [AuthScope.CHANNEL_READ_SUBSCRIPTIONS, AuthScope.MODERATOR_READ_FOLLOWERS]
REDIRECT_URI = 'http://localhost:17563'

def trigger_web_alert(event_type, textLine1, textLine2, textLine3, combined_audio_path):
    url = 'http://localhost:5000/alert'
    payload = {
        'event_type': event_type,
        'textLine1': textLine1, # Username
        'textLine2': textLine2, # TY message
        'textLine3': textLine3, # Resub message/other
        'audioFile': combined_audio_path
    }
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print('Alert triggered successfully!')
    else:
        print(f'Failed to trigger alert: {response.text}')

async def on_follow(data: ChannelFollowEvent):
    logging.info(data)
    ''' turned off
    username = data.event.user_name
    print(f'{username} just followed!')
    generate_username_audio(username)
    combined_audio_path = combine_audio(username)

    # Trigger the web-based overlay
    trigger_web_alert("follow", username, "followed", "", combined_audio_path)
    '''

async def on_subscribe(data: ChannelSubscribeEvent):
    logging.info(data)
    username = data.event.user_name

    if (data.event.is_gift): # No alert
        print(username, "got gifted a sub")
    else:
        print(f'{username} just subscribed!')
        generate_username_audio(username)
        combined_audio_path = combine_audio(username)
        textLine2 = "is a cute kitten now!"
        textLine3 = ""
        trigger_web_alert("subscribe", username, textLine2, textLine3, combined_audio_path)

async def on_gift_subscription(data: ChannelSubscriptionGiftEvent):
    logging.info(data)
    if (data.event.is_anonymous):
        username = "Anonymous"
    else:
        username = data.event.user_name
    
    gifted_number = data.event.total
    print(f'{username} gifted {gifted_number} subs')

    generate_username_audio(username)
    combined_audio_path = combine_audio(username)
    textLine2 = f'gifted {gifted_number} subs!'
    textLine3 = ""
    trigger_web_alert("giftsub", username, textLine2, textLine3, combined_audio_path)

# Test
async def on_resub(data: ChannelSubscriptionMessageEvent):
    logging.info(data)

async def start_event_listener():
    # Change the current working directory to the script's directory
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    os.chdir(script_dir)

    # Mocking events for testing (https://pytwitchapi.dev/en/stable/tutorial/mocking.html)
    test = False
    if (test):
        twitch = await Twitch(TTV_CLIENT_ID,
                            TTV_CLIENT_SECRET,
                            base_url='http://localhost:8080/mock/',
                            auth_base_url='http://localhost:8080/auth/')
        twitch.auto_refresh_auth = False
        auth = UserAuthenticator(twitch, [AuthScope.CHANNEL_READ_SUBSCRIPTIONS], auth_base_url='http://localhost:8080/auth/')
        token = await auth.mock_authenticate(TTV_USERNAME)
        await twitch.set_user_authentication(token, [AuthScope.CHANNEL_READ_SUBSCRIPTIONS])
        user = await first(twitch.get_users())
        eventsub = EventSubWebsocket(twitch,
                                    connection_url='ws://127.0.0.1:8080/ws',
                                    subscription_url='http://127.0.0.1:8080/')
        eventsub.start()
        follow_id = await eventsub.listen_channel_follow_v2(user.id, user.id, callback=on_follow)
        sub_id = await eventsub.listen_channel_subscribe(user.id, on_subscribe)
        sub_gift_id = await eventsub.listen_channel_subscription_gift(user.id, on_gift_subscription)
        resub_id = await eventsub.listen_channel_subscription_message(user.id, on_resub)

        # Test events:
        print('Test events ------------------------------------------------------------------------------------------------')
        print(f'twitch event trigger channel.follow               -t {user.id} -u {follow_id} -T websocket')
        print(f'twitch event trigger channel.subscribe            -t {user.id} -u {sub_id} -T websocket')
        print(f'twitch event trigger channel.subscription.gift    -t {user.id} -u {sub_gift_id} -T websocket')
        print(f'twitch event trigger channel.subscription.message -t {user.id} -u {resub_id} -T websocket')
        print('------------------------------------------------------------------------------------------------------------')
    else:
        # Authentication - opens webpage to authorize the app
        twitch = await Twitch(TTV_CLIENT_ID, TTV_CLIENT_SECRET)
        helper = UserAuthenticationStorageHelper(twitch, TARGET_SCOPE)
        await helper.bind()
        await twitch.authenticate_app([])
        # Get user id
        user = await first(twitch.get_users(logins=[TTV_USERNAME]))
        print('UserID: ' + user.id)
        eventsub = EventSubWebsocket(twitch)
        eventsub.start()

        # Event listeners
        follow_id = await eventsub.listen_channel_follow_v2(user.id, user.id, callback=on_follow)
        sub_id = await eventsub.listen_channel_subscribe(user.id, on_subscribe)
        sub_gift_id = await eventsub.listen_channel_subscription_gift(user.id, on_gift_subscription)
        resub_id = await eventsub.listen_channel_subscription_message(user.id, on_resub)

    try:
        input('press ENTER to stop\n')
    finally:
        await eventsub.stop()
        await twitch.close()
