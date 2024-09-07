import asyncio
from twitchAPI.oauth import UserAuthenticator, UserAuthenticationStorageHelper
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.object.eventsub import ChannelSubscribeEvent, ChannelFollowEvent
from twitchAPI.helper import first
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope

CLIENT_ID = ''
CLIENT_SECRET = ''
TTV_USERNAME = ''
TARGET_SCOPE = [AuthScope.CHANNEL_READ_SUBSCRIPTIONS, AuthScope.MODERATOR_READ_FOLLOWERS]
REDIRECT_URI = 'http://localhost:17563'


async def on_subscribe(data: ChannelSubscribeEvent):
    print(f'{data.event.user_name} just subscribed!')

async def on_follow(data: ChannelFollowEvent):
    print(f'{data.event.user_name} just followed!')

async def run():
    # Authentication - opens webpage to authorize the app
    twitch = await Twitch(CLIENT_ID, CLIENT_SECRET)
    helper = UserAuthenticationStorageHelper(twitch, TARGET_SCOPE)
    await helper.bind()
    await twitch.authenticate_app([])

    # helper.bind() alternative
    # auth = UserAuthenticator(twitch, TARGET_SCOPE, force_verify=True, url=REDIRECT_URI)
    # token, refresh_token = await auth.authenticate()
    # await twitch.set_user_authentication(token, [AuthScope.CHANNEL_READ_SUBSCRIPTIONS], refresh_token)
    # print('Token: ' + token)

    # Get user id
    user = await first(twitch.get_users(logins=[TTV_USERNAME]))
    print('UserID: ' + user.id)

    eventsub = EventSubWebsocket(twitch)
    # For testing with twitch cli - https://pytwitchapi.dev/en/stable/tutorial/mocking.html
    # eventsub = EventSubWebsocket(twitch,
    #                              connection_url='ws://127.0.0.1:8080/ws',
    #                              subscription_url='http://127.0.0.1:8080/')
    eventsub.start()

    # listen to subscribtions
    sub_id = await eventsub.listen_channel_subscribe(user.id, on_subscribe)
    # Paste this command to trigger subscribe event
    print(f'twitch event trigger channel.subscribe -t {user.id} -u {sub_id} -T websocket')
    
    # same but for follower notifications
    follow_id = await eventsub.listen_channel_follow_v2(user.id, user.id, callback=on_follow)
    print(f'twitch event trigger channel.follow -t {user.id} -u {follow_id} -T websocket')

    try:
        input('press ENTER to stop\n')
    finally:
        await eventsub.stop()
        await twitch.close()

if __name__ == '__main__':
    asyncio.run(run())