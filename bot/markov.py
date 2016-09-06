#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
import random
from collections import defaultdict
from collections import deque
class Markov:
	maximum_length = 1000
	words_that_end_in_periods = ("Mrs", "Mr", "Co", "M", "Dr", "Ms", "Sr", "St", "Rd", "Ave", "Mt", "Blvd", "Org", "Ltd")
	terminators = [".", "!", "?"]
	characters_to_remove = re.compile("[\n'\"`\”—‘’\(\):;]")
	phrase_to_remove = re.compile("BOOK .* ")

	def __init__(self, length):
		self.length = length
		self.processing_string = ""
		self.chain = defaultdict(list)

	def add_file(self, file):
		for line in file:
			self.process_line(line)
		self.process_current_string()

	def process_line(self, line):
		line = re.sub(self.characters_to_remove, '', line) + ' '
		line = re.sub(self.phrase_to_remove, '', line)

		for index in range(len(line)):
			self.processing_string += line[index]
			if line[index] in self.terminators and not line[:index].endswith(self.words_that_end_in_periods):
				self.process_current_string()

	def process_current_string(self):
		words = self.processing_string.split()
		#words = (self.length * [""]) + words + (self.length * [""])

		if words:
			self.chain[''].append(words[0])

		for index in range(len(words)):
			key_words = words[max(index - self.length, 0):index]
			for key_index in range(len(key_words)):
				words_combined = " ".join(key_words[key_index:])
				self.chain[words_combined].append(words[index])

		self.processing_string = ""

	def go_go_markov_chain(self):
		#do your thing markov chain
		key_queue = deque()
		key_queue.append('')
		result = []
		output = True
		while output and len(result) < self.maximum_length:
			output = ''
			max_number_of_words_to_try = min(self.length,len(key_queue))
			current_number_of_words_offset = max_number_of_words_to_try
			while not output and current_number_of_words_offset:
				key = " ".join(list(key_queue)[max_number_of_words_to_try - current_number_of_words_offset:])
				value = self.chain[key]
				if value:
					output = random.choice(value)
				current_number_of_words_offset -= 1
			result.append(output)
			if len(key_queue) >= self.length:
				key_queue.popleft()
			key_queue.append(output)
		return " ".join(result)

	def __str__(self):
		result = self.go_go_markov_chain()
		return result[0].upper() + result[1:]