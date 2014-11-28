#!/usr/bin/python

# Copyright (c) 2014, Brian Boylston
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import sys
import getpass
import time
import argparse
import platform

import pwhash


class TemporaryClipboard(object):

	def _macosx(self, text):
		#
		# taken from: http://stackoverflow.com/a/3555675
		#
		from AppKit import NSPasteboard, NSArray
		pb = NSPasteboard.generalPasteboard()
		pb.clearContents()
		a = NSArray.arrayWithObject_(text)
		pb.writeObjects_(a)
		def clearit():
			pb.clearContents()
		return clearit

	def _mswindows(self, text):
		#
		# taken from: http://stackoverflow.com/a/3429034
		#
		import ctypes
		strcpy = ctypes.cdll.msvcrt.strcpy
		cbopen = ctypes.windll.user32.OpenClipboard
		cbclose = ctypes.windll.user32.CloseClipboard
		cbset = ctypes.windll.user32.SetClipboardData
		cbclear = ctypes.windll.user32.EmptyClipboard
		malloc = ctypes.windll.kernel32.GlobalAlloc
		mlock  = ctypes.windll.kernel32.GlobalLock
		munlock = ctypes.windll.kernel32.GlobalUnlock
		cbopen(0)
		cbclear()
		mh = malloc(0x2000, len(text.encode('utf-8')) + 1)
		buf = mlock(mh)
		strcpy(ctypes.c_char_p(buf), text.encode('utf-8'))
		munlock(mh)
		cbset(1, mh)
		cbclose()
		def clearit():
			cbopen(0)
			cbclear()
			cbclose()
		return clearit

	def _console(self, text):
		text = text + ' '
		sys.stdout.write(text)
		def clearit():
			sys.stdout.write('\x08 \x08' * len(text))
			sys.stdout.flush()
		return clearit

	def __init__(self, text):
		self.text = text

	def __enter__(self):
		for f in [
			self._mswindows,
			self._macosx,
			self._console]:
			try:
				self.clear = f(self.text)
				return self
			except Exception:
				pass

	def __exit__(self, exc_type, exc_value, exc_trace):
		self.clear()
		return False


def maxstringlen(l):
	m = 0
	for s in l:
		n = len(s)
		if n > m:
			m = n
	return m


def wrapped(s):
	import textwrap
	return textwrap.fill(s, 78, initial_indent='   ',
		subsequent_indent='   ')


def prompt(p, d):
	r = raw_input(p + ' [' + d + ']: ')
	if r:
		return r
	else:
		return d



class NarviHelpFormatter(argparse.HelpFormatter):
	def add_arguments(self, actions):
		self._action_max_length = 0
		r = super(NarviHelpFormatter, self).add_arguments(actions)
		self._action_max_length += 2
		return r
	def _format_text(self, text):
		return '\n\n'.join(
			[super(NarviHelpFormatter, self)._format_text(t)
			for t in text.split('\n\n')])

class NarviParserError(Exception):
	def __init__(self, msg):
		self.errstr = msg

class NarviParser(argparse.ArgumentParser):
	def exit(self, status=0, message=None):
		raise NarviParserError(message)


parser = NarviParser(
	description='narvi - A password craftsman.\n\nUse narvi to manage the passwords for your multitude of online accounts.  It works like this: you provide narvi with an account identifier, such as "you@yourbank.com", and your "master" password.  narvi will generate an account-specific password based on a hash of the combination of the account identifier and your master password.\n\nChanging the account identifier, or /salt/, while keeping your master password the same will yield a different account password.  In this way, you can provide each account with a unique password while having to remember only your one master password.\n\nnarvi does not store the passwords; it generates them each time you need them.  As long as you supply the same salt and master password, the generated password will be the same each time.',
	epilog='If SUBCMD is omitted, "hash" is assumed.',
	formatter_class=NarviHelpFormatter)
subparsers = parser.add_subparsers(
	title='subcommands',
	metavar='SUBCMD')


#
#
def cmd_hash_salt_prompt(pwh, completer):
	completer.set_values(sorted(pwh.user_salts))
	saltid = raw_input('Salt: ')
	completer.clear_values()
	return saltid

def cmd_hash(args, pwh, completer):
	if args.saltid is None:
		saltid = cmd_hash_salt_prompt(pwh, completer)
	else:
		saltid = args.saltid
	if not saltid.strip():
		return
	#
	if saltid in pwh.user_salts:
		salt = pwh.user_salts[saltid]
		if salt['description']:
			print wrapped(salt['description'])
	else:
		print 'INFO:', saltid, 'not found.'
		salt = {}
		salt['value'] = saltid
		completer.set_values(sorted(pwh.hashschemes))
		salt['hashschemeid'] = prompt('Hash scheme',
			pwh.user_settings['default-hashscheme'])
		completer.set_values(sorted(pwh.wordschemes))
		salt['wordschemeid'] = prompt('Word scheme',
			pwh.user_settings['default-wordscheme'])
		completer.clear_values()
		if prompt('Save?', 'y') in ['y', 'Y']:
			saveit = True
			salt['description'] = prompt('Description', '')
			pwh.user_salts[saltid] = salt
			pwh.save_config()
	#
	while True:
		master = getpass.getpass(
			'Master password for ' + saltid + ': ')
		master2 = getpass.getpass('Again (blank if you\'re sure): ')
		if not master2 or master == master2:
			break
		else:
			print 'ERROR: Passwords do not match.'
	#
	password = pwh.generate_password(salt, master)
	#
	clipboardtime = pwh.user_settings['clipboard-time']
	with TemporaryClipboard(password):
		sys.stdout.write('.' * clipboardtime)
		sys.stdout.flush()
		for i in range(clipboardtime):
			time.sleep(1)
			sys.stdout.write('\x08 \x08')
			sys.stdout.flush()
#
def cmd_hash_completions(pwh):
	return sorted(pwh.user_salts)
#
hash_parser = subparsers.add_parser(
	'hash',
	description='Prompts for a master password and generates a password using a combination of the master password and the given SALT.  If SALT is not supplied, it is prompted for.  On Windows and Mac OS X, the generated password is temporarily copied to the clipboard; on Linux, it is temporarily displayed on the terminal.\n\nIf this is the first time that SALT has been used, narvi will prompt for the new salt\'s configuration (hash and word schemes).  During the configuration interview, default answers are shown in [brackets].',
	help='Generate a password',
	formatter_class=NarviHelpFormatter)
hash_parser.add_argument(
	'saltid',
	metavar='SALT',
	nargs='?',
	help='The SALT for which to generate a password')
hash_parser.set_defaults(func=cmd_hash)
hash_parser.completions = cmd_hash_completions


#
#
def cmd_list(args, pwh):
	for salt in sorted(pwh.user_salts):
		print salt
		if pwh.user_salts[salt]['description']:
			print wrapped(pwh.user_salts[salt]['description'])
list_parser = subparsers.add_parser(
	'list',
	description='Lists the remembered salts.',
	help='List remembered salts')
list_parser.set_defaults(func=cmd_list)


#
#
def cmd_forget(args, pwh):
	if args.saltid in pwh.user_salts:
		del pwh.user_salts[args.saltid]
		pwh.save_config()
	else:
		print 'ERROR: Salt \'' + args.saltid + '\' not found'
forget_parser = subparsers.add_parser(
	'forget',
	description='Removes the given salt SALT from the stored configuration.',
	help='Forget a salt')
forget_parser.add_argument(
	'saltid',
	metavar='SALT',
	help='The salt to be forgotten')
forget_parser.set_defaults(func=cmd_forget)
forget_parser.completions = cmd_hash_completions


#
#
def cmd_lshashschemes(args, pwh):
	for sid in sorted(pwh.hashschemes):
		print sid
		if pwh.hashschemes[sid]['description']:
			print wrapped(pwh.hashschemes[sid]['description'])
#
lshashschemes_parser = subparsers.add_parser(
	'lshashschemes',
	description='Lists the known hashing schemes.\n\nA "hash scheme" identifies a hash or key derivation function and the parameters to that function.  This key derivation function is used to generate pseudo-random bits (key material) from a combination of the salt and master password.',
	help='List available hashing schemes',
	formatter_class=NarviHelpFormatter)
lshashschemes_parser.set_defaults(func=cmd_lshashschemes)


#
#
def cmd_lswordschemes(args, pwh):
	for sid in sorted(pwh.wordschemes):
		print sid
		if pwh.wordschemes[sid]['description']:
			print wrapped(pwh.wordschemes[sid]['description'])
#
lswordschemes_parser = subparsers.add_parser(
	'lswordschemes',
	description='Lists the known word schemes.\n\nA "word scheme" identifies the method used to convert the key material output from a hash scheme into a usable password.  The word scheme defines the character set used (letters, digits, etc.), the password length, and any complexity requirements.',
	help='List available word schemes',
	formatter_class=NarviHelpFormatter)
lswordschemes_parser.set_defaults(func=cmd_lswordschemes)


#
#
def cmd_license(args, pwh):
	sys.stdout.write(__loader__.get_data('LICENSE.md'))
license_parser = subparsers.add_parser(
	'license',
	description='Outputs the license(s).',
	help='Output the license(s)')
license_parser.set_defaults(func=cmd_license)


#
#
def cmd_help(args, pwh):
	if args.subcmd:
		global subparsers
		subparsers._name_parser_map[args.subcmd].print_help()
	else:
		global parser
		parser.print_help()
#
def cmd_help_completions(pwh, sp=subparsers):
	return sp._name_parser_map.keys()
#
help_parser = subparsers.add_parser(
	'help',
	description='Displays general help or, if SUBCMD is given, help for SUBCMD.',
	help='Display help')
help_parser.add_argument(
	'subcmd',
	metavar='SUBCMD',
	help='The SUBCMD for which to display help',
	nargs='?',
	choices=subparsers._name_parser_map.keys())
help_parser.set_defaults(func=cmd_help)
help_parser.completions = cmd_help_completions



# configure readline
#
class PromptCompleter(object):
	def __init__(self):
		self._values = []
	def complete(self, text, state):
		for v in self._values:
			if v.startswith(text):
				if state > 0:
					state -= 1
				else:
					return v
		return None
	def set_values(self, values):
		self._values = values
		readline.clear_history()
		for v in reversed(self._values):
			readline.add_history(v)
	def clear_values(self):
		self._values = []
		readline.clear_history()
class NoCompleter(object):
	def set_values(self, values):
		pass
	def clear_values(self):
		pass
#
try:
	if platform.system().lower() == 'windows':
		from pyreadline.rlmain import Readline
		import pyreadline.console as console
		readline = Readline()
		console.install_readline(readline.readline)
	else:
		import readline
except:
	completer = NoCompleter()
	readline = None
else:
	completer = PromptCompleter()
	readline.set_completer(completer.complete)
	#
	if 'libedit' in readline.__doc__:
		readline.parse_and_bind('bind ^I rl_complete')
		readline.parse_and_bind('bind ^F em-inc-search-prev')
		readline.parse_and_bind('bind ^R em-inc-search-next')
		# hack for the equivalent of set_completer_delims():
		import ctypes
		readline.my_completer_delims = ctypes.create_string_buffer(' ')
		brkchars = ctypes.c_char_p.in_dll(ctypes.CDLL('libedit.dylib'),
			'rl_basic_word_break_characters')
		brkchars.value = ctypes.addressof(readline.my_completer_delims)
	else:
		readline.parse_and_bind('tab: complete')
		readline.parse_and_bind('Control-f: reverse-search-history')
		readline.parse_and_bind('Control-r: forward-search-history')
		readline.set_completer_delims(' ')


#
#
def interactive(parser, prompt, pwh, completer):
	# start with hash
	saltid = cmd_hash_salt_prompt(pwh, completer)
	if saltid.strip():
		args = parser.parse_args(['hash', saltid])
		return args.func(args, pwh, completer)
	#
	import shlex
	global readline
	#
	icomplete_choices = []
	def icomplete(text, state):
		global icomplete_choices
		subparser = parser._subparsers._actions[1]
		if state == 0 and readline.get_begidx() == 0:
			subcmds = subparser._name_parser_map.keys()
			subcmds.append('quit')
			choices = sorted(subcmds)
		elif state == 0:
			argv = shlex.split(readline.get_line_buffer())
			subcmd = subparser._name_parser_map[argv[0]]
			if hasattr(subcmd, 'completions'):
				choices = subcmd.completions(pwh)
		if state == 0:
			icomplete_choices = [c for c in choices if c.startswith(text)]
		try:
			return icomplete_choices[state]
		except IndexError:
			return None
	#
	while True:
		#
		if readline:
			oldcompleter = readline.get_completer()
			readline.set_completer(icomplete)
		else:
			oldcompleter = None
		try:
			l = raw_input(prompt)
		except KeyboardInterrupt:
			sys.stdout.write('\n')
			continue
		finally:
			if oldcompleter:
				readline.set_completer(oldcompleter)
		#
		if l == 'quit':
			return
		argv = shlex.split(l)
		if len(argv) == 0:
			continue
		try:
			args = parser.parse_args(argv)
		except NarviParserError as e:
			if e.errstr:
				print e.errstr
		else:
			try:
				if args.func == cmd_hash:
					args.func(args, pwh, completer)
				else:
					args.func(args, pwh)
			except KeyboardInterrupt:
				sys.stdout.write('\n')



try:
	pwh = pwhash.PWHash('.narvi')
	if len(sys.argv) == 1:
		interactive(parser, 'narvi> ', pwh, completer)
	else:
		try:
			args = parser.parse_args()
		except NarviParserError as e:
			if e.errstr:
				sys.stderr.write(e.errstr)
			sys.exit(2)
		else:
			if args.func == cmd_hash:
				args.func(args, pwh, completer)
			else:
				args.func(args, pwh)
except KeyboardInterrupt:
	sys.stderr.write('\nInterrupted.\n')
	sys.exit(1)



