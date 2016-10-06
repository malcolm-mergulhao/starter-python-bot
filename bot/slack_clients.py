
import logging
import re
import time
import random
import os.path

from slacker import Slacker
from slackclient import SlackClient
from messenger import Messenger

logger = logging.getLogger(__name__)


class SlackClients(object):
    def __init__(self, token):
        self.token = token

        # Slacker is a Slack Web API Client
        self.web = Slacker(token)

        # SlackClient is a Slack Websocket RTM API Client
        self.rtm = SlackClient(token)

        self.msg_writer = Messenger(self)

    def bot_user_id(self):
        return self.rtm.server.login_data['self']['id']

    def is_message_from_me(self, message):
        is_from_me = False
        me = self.bot_user_id()
        if 'user' in message and message['user'] == me:
            is_from_me = True
        elif 'subtype' in message and message['subtype'] == "bot_message":
            is_from_me = True
        # if 'bot_id' in message and message['bot_id'] == 'B1S057DV0':
        #     is_from_me = True
        return is_from_me

    def is_bot_mention(self, message):
        bot_user_name = self.rtm.server.login_data['self']['id']
        if re.search("@{}".format(bot_user_name), message):
            return True
        else:
            return False

    def send_user_typing_pause(self, channel_id, sleep_time=3.0):
        user_typing_json = {"type": "typing", "channel": channel_id}
        self.rtm.server.send_to_websocket(user_typing_json)
        time.sleep(sleep_time)

    # this method only gets a team's custom emojis and NOT all slack emojis
    def get_random_emoji(self):
        response = self.rtm.api_call('emoji.list')
        emojis = response['emoji'].items()
        return emojis[int(random.random()*len(emojis))][0]

    def send_message_as_other(self, channel_id, msg, name, emoji):
        return self.rtm.api_call(
            'chat.postMessage', token=str(self.token), channel=channel_id,
            text=msg, link_names=1, username=name, unfurl_links=True,
            icon_emoji=emoji
        )

    def send_message(self, channel_id, msg):
        return self.rtm.api_call(
            'chat.postMessage', token=str(self.token), channel=channel_id,
            text=msg, as_user=True, link_names=1, unfurl_links=True
        )

    def update_message(self, channel_id, timestamp, updated_msg):
        return self.rtm.api_call(
            'chat.update', token=str(self.token), channel=channel_id,
            text=updated_msg, as_user=True, link_names=1, unfurl_links=True,
            ts=timestamp
        )

    def get_message_history(self, channel_id, count=None):
        response = self.rtm.api_call(
            'channels.history', token=str(self.token), channel=channel_id,
            count=count
        )
        if 'error' in response:
            error_msg = "`get_message_history` error:\n" + str(response)
            self.msg_writer.write_error(error_msg)
        return response

    def delete_message(self, channel_id, timestamp):
        response = self.rtm.api_call(
            'chat.delete', token=str(self.token), channel=channel_id,
            as_user=True, ts=timestamp
        )
        if 'error' in response:
            error_msg = "`delete_message` error:\n" + str(response)
            self.msg_writer.write_error(error_msg)
        return response

    def send_attachment(self, channel_id, txt, attachment):
        # this does not return the response object that rtm does
        return self.web.chat.post_message(
            channel_id, txt, attachments=[attachment], as_user='true'
        )

    def get_users(self):
        return self.rtm.api_call('users.list', token=str(self.token))

    def get_channels(self):
        return self.rtm.api_call('channels.list', token=str(self.token))

    def get_groups(self):
        return self.rtm.api_call('groups.list', token=str(self.token))

    def get_ims(self):
        return self.rtm.api_call('im.list', token=str(self.token))

    def send_reaction(self, emoji_name, channel_id, timestamp):
        return self.rtm.api_call(
            "reactions.add", token=str(self.token), name=emoji_name,
            channel=channel_id, timestamp=timestamp
        )

    def upload_file_to_slack(self, filepath, filename, channel):
        my_file = os.path.join(filepath, filename)
        return self.web.files.upload(my_file, channels=channel)
