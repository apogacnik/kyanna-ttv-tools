from config import TTV_CLIENT_ID, TTV_CLIENT_SECRET, TTV_USERNAME
from audio.generate_username_audio import generate_username_audio
from audio.combine_audio import combine_audio

from twitchAPI.twitch import Twitch
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.object.eventsub import ChannelSubscribeEvent, ChannelFollowEvent
from twitchAPI.type import AuthScope
from twitchAPI.helper import first
import requests

import logging
import os
from datetime import datetime

TARGET_SCOPE = [AuthScope.CHANNEL_READ_SUBSCRIPTIONS, AuthScope.MODERATOR_READ_FOLLOWERS]
REDIRECT_URI = 'http://localhost:17563'

# Set up logging
log_folder = 'logs/'
os.makedirs(log_folder, exist_ok=True)  # Create the folder if it doesn't exist
current_date = datetime.now().strftime('%Y-%m-%d')
log_filename = f'{log_folder}{current_date}.log'

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO, 
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def trigger_web_alert(username, combined_audio_path):
    url = 'http://localhost:5000/alert'
    payload = {
        'username': username,
        'audioFile': combined_audio_path
    }
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print('Alert triggered successfully!')
    else:
        print(f'Failed to trigger alert: {response.text}')

async def on_subscribe(data: ChannelSubscribeEvent):
    username = data.event.user_name
    print(f'{username} just subscribed!')
    logging.info(data)
    generate_username_audio(username)
    combined_audio_path = combine_audio(username)

    # Trigger the web-based overlay
    trigger_web_alert(username, combined_audio_path)

async def on_follow(data: ChannelFollowEvent):
    username = data.event.user_name
    print(f'{username} just followed!')
    logging.info(data)
    generate_username_audio(username)
    combined_audio_path = combine_audio(username)

    # Trigger the web-based overlay
    trigger_web_alert(username, combined_audio_path)

async def start_event_listener():
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

    # listen to subscribtions
    sub_id = await eventsub.listen_channel_subscribe(user.id, on_subscribe)
    # listen for followers
    follow_id = await eventsub.listen_channel_follow_v2(user.id, user.id, callback=on_follow)

    try:
        input('press ENTER to stop\n')
    finally:
        await eventsub.stop()
        await twitch.close()
