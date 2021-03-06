import time
import logging
import traceback
import os

from slack_clients import SlackClients
from messenger import Messenger
from event_handler import RtmEventHandler
from time_triggered_event_manager import TimeTriggeredEventManager
from markov import Markov
import config_manager

logger = logging.getLogger(__name__)


def spawn_bot():
    return SlackBot()


class SlackBot(object):
    def __init__(self, token=None):
        """Creates Slacker Web and RTM clients with API Bot User token.

        Args:
            token (str): Slack API Bot User token
            (for development token set in env)
        """
        self.last_ping = 0
        self.keep_running = True
        if token is not None:
            self.clients = SlackClients(token)

    def start(self, resource):
        """Creates Slack Web and RTM clients for the given Resource
        using the provided API tokens and configuration, then
        connects websocket and listens for RTM events.

        Args:
            resource (dict of Resource JSON): See message payloads:
            https://beepboophq.com/docs/article/resourcer-api
        """
        logger.info('Starting bot for resource: {}'.format(resource))
        if ('resource' in resource and
                'SlackBotAccessToken' in resource['resource']):
            res_access_token = resource['resource']['SlackBotAccessToken']
            self.clients = SlackClients(res_access_token)

        if self.clients.rtm.rtm_connect():
            logging.info(
                u'Connected {} to {} team at https://{}.slack.com'.format(
                    self.clients.rtm.server.username,
                    self.clients.rtm.server.login_data['team']['name'],
                    self.clients.rtm.server.domain
                )
            )

            msg_writer = Messenger(self.clients)

            # Random markov here
            markov_chain = Markov(3, msg_writer)

            config_manager.start_config_loader()

            event_handler = RtmEventHandler(
                self.clients, msg_writer, markov_chain
            )
            time_event_handler = TimeTriggeredEventManager(
                self.clients, msg_writer, markov_chain
            )

            os.chmod('./scripts/make_config.sh', 0755)

            while self.keep_running:
                for event in self.clients.rtm.rtm_read():
                    try:
                        event_handler.handle(event)
                    except:
                        err_msg = traceback.format_exc()
                        logging.error('Unexpected error: {}'.format(err_msg))
                        msg_writer.write_error(err_msg, event['channel'])
                        continue

                self._auto_ping(time_event_handler)
                time.sleep(.1)
        else:
            logger.error(
                'Failed to connect to RTM client with token: {}'.format(
                    self.clients.token
                )
            )

    def _auto_ping(self, time_event_handler):
        # hard code the interval to 10 seconds
        now = int(time.time())
        if now > self.last_ping + 10:
            self.clients.rtm.server.ping()
            self.last_ping = now
            time_event_handler.trigger_timed_event()

    def stop(self, resource):
        """Stop any polling loops on clients, clean up any resources,
        close connections if possible.

        Args:
            resource (dict of Resource JSON): See message payloads:
            https://beepboophq.com/docs/article/resourcer-api
        """
        self.keep_running = False
