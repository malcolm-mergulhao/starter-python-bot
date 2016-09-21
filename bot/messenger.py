# coding=utf-8

import logging
import random
import re
import os.path
import xkcd_manager
import weather_manager
from datetime import datetime
from loud_manager import LoudManager
from whos_that_pokemon_manager import WhosThatPokemonManager
from pokemon_caster import PokemonCaster
from hogwarts_house_sorter import HogwartsHouseSorter
import scripts.weather_controller
from scripts.weather_controller import WeatherController
from sass_manager import SassManager
from food_getter import FoodGetter
from explanation_manager import ExplanationManager
from apology_manager import ApologyManager
from equation_manager import EquationManager

logger = logging.getLogger(__name__)


class Messenger(object):
    def __init__(self, slack_clients):
        self.clients = slack_clients
        self.loud_manager = LoudManager()
        self.whos_that_pokemon_manager = WhosThatPokemonManager()
        self.pokemon_caster = PokemonCaster()
        self.hogwarts_house_sorter = HogwartsHouseSorter()
        self.sass_manager = SassManager()
        self.apology_manager = ApologyManager()
        self.food_getter = FoodGetter()
        self.explanation_manager = ExplanationManager()
        self.equation_manager = EquationManager()
        self.user_dict = {}

    def send_message(self, channel_id, msg):
        # in the case of Group and Private channels, RTM channel payload
        # is a complex dictionary
        if isinstance(channel_id, dict):
            channel_id = channel_id['id']
        # logger.debug(
        #   'Sending msg: {} to channel: {}'.format(msg, channel_id)
        # )
        channel = self.clients.rtm.server.channels.find(channel_id)
        channel.send_message(msg)

    def write_custom_error(self, msg):
        self.send_message('C1SDALDG9', msg)

    def write_slow(self, channel_id, msg):
        self.clients.send_user_typing_pause(channel_id)
        self.send_message(channel_id, msg)

    def write_closing(self):
        closing_msgs = ["No!! Don't kill me! I want to live!", "Good BYEEE!!!",
                        "I'm dying again :sob:",
                        "Have you gotten tired of this face :zacefron: ?"]
        txt = random.choice(closing_msgs)
        self.send_message('C1SDALDG9', txt)

    def write_dont_talk(self, channel_id, user_id, timestamp):
        if user_id in self.user_dict:
            if float(self.user_dict[user_id]) + 600 >= float(timestamp):
                txt = 'PSSST... no talking in the announcements channel!'
                self.send_message(channel_id, txt)
        self.user_dict[user_id] = timestamp

    def write_message_deleted(self, channel_id):
        txt = 'I SAW THAT'
        self.send_message(channel_id, txt)

    def write_left_channel(self, channel_id):
        txt = '...well THAT was something'
        self.send_message(channel_id, txt)

    def write_joined_channel(self, channel_id, user_id):
        if channel_id == 'C171ASJJK' or channel_id == 'C1SDALDG9':
            txt = 'Hey <@{}>! Welcome to the Testing (aka the Weather) channel. Please MUTE this channel or be inundaded with notifications!'.format(user_id)
            self.clients.send_user_typing_pause(channel_id)
            self.send_message(channel_id, txt)
            self.write_xkcd(channel_id, "15")
        else:
            self.write_greeting(channel_id, user_id)

    def write_help_message(self, channel_id):
        bot_uid = self.clients.bot_user_id()
        help_txt = [ "> `hi <@" + bot_uid + ">` - I'll greet back, i don't bite. :wave:",
            "> `<@" + bot_uid + "> joke` - I'll tell you one of my finest jokes, with a typing pause for effect. :laughing:",
            "> `<@" + bot_uid + "> weather` - Let me tell you the weather in Winnipeg. :rainbow:",
            "> `<@" + bot_uid + "> I'm sad` - Maybe I can cheer you up. :wink:",
            "> `<@" + bot_uid + "> sort me` - I'll sort you into one of the four Hogwarts houses! Better hope you don't get :slytherin:",
            "> `<@" + bot_uid + "> apologize` - Sometimes I make mistakes. Tell me when I do so I can apologize. :bow:",
            "> `<@" + bot_uid + "> thanks!` - I also sometimes do well! I also like to be appreciated :innocent:",
            "> `<@" + bot_uid + "> solve <equation>` - Math sucks. I can help! :nerd_face:",
            "> `<@" + bot_uid + "> sass <name>` - I'll be sure to sass <name> until the sun burns out. :smiling_imp:",
            "> `<@" + bot_uid + "> good morning` - I shall wish you a good morning as well! :sunny:",
            "> `<@" + bot_uid + "> good night` - I'll give you a goodnight greeting :crescent_moon:",
            "> `<@" + bot_uid + "> who's that pokemon?` - Are you a pokemon master? :slowpoke:",
            "> `<@" + bot_uid + "> Explain | Why` - I'll explain what's going on. :reginageorge:",
            "> `<@" + bot_uid + "> french <phrase>` - I know flawless French! I'll translate for you :bombardier:",
            "> `<@" + bot_uid + "> marry me` - ...Are you going to propose to me?? _Le gasp_ :le gasp:",
            "> `<@" + bot_uid + "> sweetpotato me` - Sometimes you just need a :sweet_potato:",
            "> `Boyer` - Did you know Gord Boyer is my favourite prof? I'll give you one of his wise quotes :nerd_face:",
            "> `Crying` - I cry when you cry :joy:",
            "> `Wiener` - You wanna know who a wiener is? I'll tell you :eggplant:",
            "> `<pokemon> I choose you!` - Are you going to be the very best? :yourturn:",
            "> `encourage` - Let me help you get back on track. :grinning:",
            "> `hungry | feed` - Have some food courtesy of moi :banana:",
            "> `Fuck this` - You're referring to OS, aren't you? Don't worry I got just the video. :+1:",
            "> `Just Do it` - Need some motivation? This vid should do the trick :sunglasses:",
            "> `Pigeon Mode` - Want a pigeon sound? Type a sentence with 'coo ' in it.",
            "> `XKCD` - Want an XKCD comic? Type it's number to get it, or leave it blank to get the latest one",
            "> `TicTacToe` - Want to play TicTacToe? Type 'TicTacToe help' for more information"]
        txt = "I'm Zac Efron.  I'll *_respond_* to the following {0} commands:\n".format(len(help_txt))
        for val in range(len(help_txt)):
            txt += help_txt[val]
            txt += '\n'

        self.clients.send_user_typing_pause(channel_id)
        self.send_message(channel_id, txt)

    def write_to_french(self, channel_id, msg):
        self.clients.send_user_typing_pause(channel_id)
        msg = msg.lower()
        msg = msg.replace('zac', '')
        msg = msg.replace('french', '')
        tokens = msg.split()
        response = ' '.join(tokens)
        txt = '_le {}_'.format(response)
        self.send_message(channel_id, txt)

    def write_greeting(self, channel_id, user_id):
        self.clients.send_user_typing_pause(channel_id)
        greetings = ['Hi', 'Hello', 'Nice to meet you', 'Howdy', 'Salutations']
        txt = '{}, <@{}>!'.format(random.choice(greetings), user_id)
        self.send_message(channel_id, txt)

    def write_good_night(self, channel_id, user_id):
        self.clients.send_user_typing_pause(channel_id)
        good_nights = ['Goodnight', ':crescent_moon: Good night', 'Goodnight, my dear', 'Sweet dreams', 'Don\'t let the bed bugs bite',
        'Pleasant dreams', 'Sleep well', 'Until tomorrow then', 'May your dreams be filled with my beautiful face :zacefron:']
        txt =txt = '{}, <@{}>!'.format(random.choice(good_nights), user_id)
        self.send_message(channel_id, txt)

    def write_spelling_mistake(self, channel_id):
        self.clients.send_user_typing_pause(channel_id)
        txt = 'Spelft it wronbg again I see...'
        self.send_message(channel_id, txt)

    def write_prompt(self, channel_id):
        self.clients.send_user_typing_pause(channel_id)
        bot_uid = self.clients.bot_user_id()
        txt = "I'm sorry, I didn't quite understand... Can I help you? (e.g. `<@" + bot_uid + "> help`)"
        self.send_message(channel_id, txt)

    def write_joke(self, channel_id):
        self.clients.send_user_typing_pause(channel_id)
        question = "Why did the python cross the road?"
        self.send_message(channel_id, question)
        self.clients.send_user_typing_pause(channel_id)
        answer = "To eat the chicken on the other side! :laughing:"
        self.send_message(channel_id, answer)

    def write_encouragement(self, channel_id, user_id):
        self.clients.send_user_typing_pause(channel_id)
        self.send_message(channel_id, 'Get your shit together <@{0}>'.format(user_id))

    def write_food(self, channel_id):
        self.clients.send_user_typing_pause(channel_id)
        food = self.food_getter.get_random_food()
        self.send_message(channel_id, food)

    def write_bang(self, channel_id, user_id):
        self.clients.send_user_typing_pause(channel_id)
        bang = 'BANG you\'re dead <@{}> :gun:'.format(user_id)
        self.send_message(channel_id, bang)

    def write_cast_pokemon(self, channel_id, msg):
        pkmn = self.pokemon_caster.i_choose_you(msg)
        if pkmn is not None:
            self.send_message(channel_id, pkmn)

    def write_whos_that_pokemon(self, channel_id):
        self.send_message(channel_id, self.whos_that_pokemon_manager.whos_that_pkmn())

    def write_pokemon_guessed_response(self, channel_id, user_id, msg):
        result = self.whos_that_pokemon_manager.check_response(user_id, msg)
        if result is not None:
            self.send_message(channel_id, result)

    def write_error(self, channel_id, err_msg):
        txt = ":face_with_head_bandage: my maker didn't handle this error very well:\n>```{}```".format(err_msg)
        self.send_message(channel_id, txt)

    def write_sad(self, channel_id):
        self.clients.send_user_typing_pause(channel_id)
        txt = "This always cracks me up. :wink:"
        self.send_message(channel_id, txt)
        self.clients.send_user_typing_pause(channel_id)
        attachment = {
            "title": "/giphy bloopin",
            "title_link": "http://giphy.com/gifs/friday-rebecca-black-hurrr-13FsSYo3fzfT2g",
            "image_url": "http://i.giphy.com/13FsSYo3fzfT2g.gif",
            "color": "#7CD197",
        }
        self.clients.web.chat.post_message(channel_id,"", attachments=[attachment], as_user='true')
        txt = "I'm crying into my tea. :joy:"
        self.clients.send_user_typing_pause(channel_id)
        self.send_message(channel_id, txt)

    def demo_attachment(self, channel_id):
        txt = "Beep Beep Boop is a ridiculously simple hosting platform for your Slackbots."
        attachment = {
            "pretext": "We bring bots to life. :sunglasses: :thumbsup:",
            "title": "Host, deploy and share your bot in seconds.",
            "title_link": "https://beepboophq.com/",
            "text": txt,
            "fallback": txt,
            "image_url": "https://storage.googleapis.com/beepboophq/_assets/bot-1.22f6fb.png",
            "color": "#7CD197",
        }
        self.clients.web.chat.post_message(channel_id, txt, attachments=[attachment], as_user='true')

    def write_weather(self, channel_id):
        # line1 = WeatherController.get_weather()
        line1 = "Sorry, I don't know the weather today :zacefron: "
        line2 = "Anyways, it's always hot when I'm around :sunglasses: "
        #self.send_message(channel_id, line1)

        #response = WeatherController.get_weather()
        response = weather_manager.getCurrentWeather()
        self.clients.send_user_typing_pause(channel_id)
        self.send_message(channel_id, response)
        #self.send_message(channel_id, line2)

    def write_loud(self, channel_id, origMessage):
        self.loud_manager.write_loud_to_file(origMessage)
        if random.random() == random.random():
            self.send_message(channel_id, self.loud_manager.get_random_loud())

    def write_hogwarts_house(self, channel_id, user_id, msg):
        self.clients.send_user_typing_pause(channel_id)
        response = self.hogwarts_house_sorter.sort_into_house(msg)
        txt = '<@{}>: {}'.format(user_id, response)
        self.send_message(channel_id, txt)

    def write_explanation(self, channel_id):
        self.clients.send_user_typing_pause(channel_id)
        self.send_message(channel_id, self.explanation_manager.get_explanation())

    def write_sass(self, channel_id, msg):
        self.clients.send_user_typing_pause(channel_id)
        txt = self.sass_manager.get_sass(msg)
        self.send_message(channel_id, txt)

    def write_apology(self, channel_id):
        self.clients.send_user_typing_pause(channel_id)
        self.send_message(channel_id, self.apology_manager.get_random_apology())

    def write_solution(self, channel_id, msg):
        self.clients.send_user_typing_pause(channel_id)
        self.send_message(channel_id, self.equation_manager.solve(msg))

    def write_sweetpotato_me(self, channel_id, user_id):
        self.clients.send_user_typing_pause(channel_id)
        txt = 'Here, <@{}>! :sweet_potato:'.format(user_id)
        self.send_message(channel_id, txt)

    def write_marry_me(self, channel_id):
        self.clients.send_user_typing_pause(channel_id)
        responses = ['OKAY! :ring:', 'Ummm, how \'bout no.', 'Shoot I would...if you were :kiera:', '_le shrug_ \'k.',
                'R-Really? Okay, I shall be your ~bride~ husband from now on!!', 'Sorry but I\'m already married to my job.',
                'Sorry, but I\'m already married to :nicole:', 'HOW DO I KNOW YOU WON\'T CHEAT ON ME WITH QBOT?!??',
                '_le HELLS YES!_', 'Sorry, but you are human, and I am a mere bot. It could never work out between us...',
                ':musical_note: _IF YOU LIKE IT THEN YOU SHOULDA PUT A RING ON IT_ :musical_note:', 'No. Never. Nope. Nu-uh.']
        txt = '{}'.format(random.choice(responses))
        self.send_message(channel_id, txt)


    def write_draw_me(self, channel_id):
        self.clients.send_user_typing_pause(channel_id)
        file = open(os.path.join('./resources', 'draw_me.txt'), 'r')
        urls = file.read().splitlines()
        txt = '{}'.format(random.choice(urls))
        self.send_message(channel_id, txt)

    def write_forever(self, channel_id):
        self.clients.send_user_typing_pause(channel_id)
        file = open(os.path.join('./resources', 'forever.txt'), 'r')
        comments = file.read().splitlines()
        txt = '{}'.format(random.choice(comments))
        self.send_message(channel_id, txt)
        self.clients.send_user_typing_pause(channel_id)
        answer = '{}'.format('Just kidding! :laughing:')
        self.send_message(channel_id, answer)
        self.clients.send_user_typing_pause(channel_id)
        #random_custom_emoji = self.clients.get_random_emoji()
        random_custom_emoji = 'trollface'
        emoji =':{}:'.format(random_custom_emoji)
        self.send_message(channel_id, emoji)

    def write_story(self, channel_id):
        self.clients.send_user_typing_pause(channel_id)
        self.send_message(channel_id, "STORY TIME")
        self.clients.send_user_typing_pause(channel_id)
        starts = ['Once upon a time', 'In the beginning', 'A long time ago']
        protagonists = ['boys', 'girls', 'dragons', 'helicopter wolves', 'programmers', 'birds', 'humans', 'human-beings', 'relatives', 'friends', 'doctors']
        locations = ['heights of a mountain', 'depghts of the ocean', 'sandiest beach of all time', 'most amazing wizard convention that has ever existed', 'smoky cauldron next door', 'alphabet']
        start_txt = '{} there were two {} located in the {}...'.format(random.choice(starts), random.choice(protagonists), random.choice(locations))
        self.send_message(channel_id, start_txt)
        dialougue = ["\"Is it really?\"", "\"Absolutely. I'm awfully sorry about the odor though. That must bother you.\"", "\"Don't! Please don't.\"", "\"But _look_ at them!\"", "\"I'm only talking\"", "\"It's much easier if I talk. But I don't want to bother you.\"",
                    "\"You know it doesn't bother me\"", "\"Please tell me what I can do. There must be something I can do.\"", "\"You might think about some one else.\"", "\"I don't mean that.\"", "\"You do it. I'm too tired.\"", "\"Anything you do too bloody long.\"",
                    "\"Do you feel anything strange?\"", "\"No. Just a little sleepy.\"", "\"You know the only thing I've never lost is curiosity.\"", "\"Tell it to go away.\"",  "\"What's the matter?\"", "\"I don't really care about it, you know.\"", "\"What about the tea?\"",
                    "\"Why nothing.\"", "\"Why what, dear?\"", "\"You tell them why\"", "\"It's not good for you.\"", "\"I never learned.\"", "\"That's all right.\""]
        for i in range(8):
            txt = random.choice(dialougue)
            self.clients.send_user_typing_pause(channel_id)
            self.send_message(channel_id, txt)
        conclusions = ["Then they went home.", "Then they went home and lived happily ever after.", "Then a witch swooped down and killed them.", "Then a truck ran over them", 'Then they lived happily ever after']
        end_txt = random.choice(conclusions)
        self.clients.send_user_typing_pause(channel_id)
        self.send_message(channel_id, end_txt)
        self.clients.send_user_typing_pause(channel_id)
        self.send_message(channel_id, "THE END")

    def write_flip(self, channel_id):
        self.send_message(channel_id, u"(╯°□°）╯︵ ┻━┻")

    def write_unflip(self, channel_id):
        self.send_message(channel_id, u"┬─┬ノ( º _ ºノ)")

    def write_sup_son(self, channel_id):
        self.send_message(channel_id, u"¯\_(ツ)_/¯")

    def write_riri_me(self, channel_id, msg):
        riri_flag = re.compile('riri[a-z]* ')
        token = re.split(riri_flag, msg.lower())
        if len(token) > 1:
            target = token[1]
            target = target.upper()
        else:
            target = "WHY WOULD YOU JUST TYPE RIRI?\n"
        txt = ' '.join(target for num in range(5))
        self.clients.send_user_typing_pause(channel_id)
        self.send_message(channel_id, txt)

    def write_xkcd(self, channel_id, msg):
        self.clients.send_user_typing_pause(channel_id)
        txt = xkcd_manager.getImageLocation(msg)
        self.send_message(channel_id, txt)
