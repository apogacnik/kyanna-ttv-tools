from config import TTV_CLIENT_ID, TTV_CLIENT_SECRET, TTV_USERNAME
from audio.generate_username_audio import generate_username_audio
from audio.combine_audio import combine_audio

from twitchAPI.twitch import Twitch
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.object.eventsub import ChannelSubscribeEvent, ChannelFollowEvent
from twitchAPI.type import AuthScope
from twitchAPI.helper import first

TARGET_SCOPE = [AuthScope.CHANNEL_READ_SUBSCRIPTIONS, AuthScope.MODERATOR_READ_FOLLOWERS]
REDIRECT_URI = 'http://localhost:17563'


async def on_subscribe(data: ChannelSubscribeEvent):
    print(f'{data.event.user_name} just subscribed!')
    generate_username_audio(data.event.user_name)
    combine_audio(data.event.user_name)

async def on_follow(data: ChannelFollowEvent):
    print(f'{data.event.user_name} just followed!')
    generate_username_audio(data.event.user_name)
    combine_audio(data.event.user_name)

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
