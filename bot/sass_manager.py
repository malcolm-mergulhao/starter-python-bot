import os.path
import random

class SassManager(object):
	
    def __init__(self):
        self.sass_file = open('sass.txt', 'r')
        self.sass_cache = list()
        self.cache_loaded = False

    def load_sass_cache():
        for line in self.sass_file.read().splitlines():
            self.sass_cache.append(line)

    def get_sass(msg):
        return self.format_sass(self, msg)

    def format_sass(msg):
        target = self.get_target(msg)
        sass = self.get_random_sass(self)
        return "Hey, " + target + "! " + sass

    def get_random_sass():
        if not self.cache_loaded:
            self.load_sass_cache()
            self.cache_loaded = True

    def get_target(msg):
        tokens = msg.split("sass ")
        target = self.format_target(target.lower())

    def format_target(target):
        if target is "me":
            return "you"
        elif target is "yourself":
            return "Zac Efron"
        else:
            return target