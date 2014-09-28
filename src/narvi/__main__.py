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

import pwhash


class TemporaryClipboard(object):

	def _macosx(self, text):
		from AppKit import NSPasteboard, NSArray
		pb = NSPasteboard.generalPasteboard()
		pb.clearContents()
		a = NSArray.arrayWithObject_(text)
		pb.writeObjects_(a)
		def clearit():
			pb.clearContents()
		return clearit

	def _mswindows(self, text):
		import ctypes
		strcpy = ctypes.cdll.msvcrt.strcpy
		cbopen = ctypes.windll.user32.OpenClipboard
		cbclose = ctypes.windll.user32.CloseClipboard
		cbpaste = ctypes.windll.user32.SetClipboardData
		cbclear = ctypes.windll.user32.EmptyClipboard
		malloc = ctypes.windll.kernel32.GlobalAlloc
		mlock  = ctypes.windll.kernel32.GlobalLock
		munlock = ctypes.windll.kernel32.GlobalUnlock
		cbopen(None)
		cbclear()
		mh = malloc(0x2000, len(text.encode('utf-8')) + 1)
		buf = mlock(mh)
		strcpy(ctypes.c_char_p(buf), text.encode('utf-8'))
		munlock(mh)
		cbpaste(1, mh)
		cbclose()
		def clearit():
			cbopen(None)
			cbclear()
			cbclose()
		return clearit

	def _console(self, text):
		raise Exception('not implemented')

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


def prompt(p, d):
	r = raw_input(p + ' [' + d + ']: ')
	if r:
		return r
	else:
		return d



parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()


#
#
def cmd_hash(args, pwh):
	if args.saltid is None:
		saltid = raw_input('Salt: ')
	else:
		saltid = args.saltid
	if saltid in pwh.user_salts:
		salt = pwh.user_salts[saltid]
		while True:
			master = getpass.getpass(
				'Master password for ' + saltid + ': ')
			password, checksum = pwh.generate_password(
				salt, master)
			if (salt['checksum'] is None or
				checksum == salt['checksum']):
				break
			else:
				print 'ERROR: Checksum does not match.'
	else:
		print 'INFO:', saltid, 'not found.'
		salt = {}
		salt['value'] = saltid
		salt['hashschemeid'] = prompt('Hash scheme',
			pwh.user_settings['default-hashscheme'])
		salt['wordschemeid'] = prompt('Word scheme',
			pwh.user_settings['default-wordscheme'])
		if prompt('Save?', 'y') in ['y', 'Y']:
			saveit = True
			salt['description'] = prompt('Description', '')
			while True:
				master = getpass.getpass(
					'Master password for ' + saltid + ': ')
				if pwh.user_settings['store-checksum']:
					master2 = getpass.getpass('Again: ')
					if master == master2:
						break
					else:
						print 'ERROR: Passwords do not match.'
				else:
					salt['checksum'] = None
					break
		else:
			saveit = False
			master = getpass.getpass(
				'Master password for ' + saltid + ': ')
		if saveit:
			pwh.save_config()
		password, checksum = pwh.generate_password(
			salt, master)
		if saveit:
			if pwh.user_settings['store-checksum']:
				salt['checksum'] = checksum
			else:
				salt['checksum'] = None
			pwh.user_salts[saltid] = salt
			pwh.save_config()
	clipboardtime = pwh.user_settings['clipboard-time']
	with TemporaryClipboard(password):
		sys.stdout.write('.' * clipboardtime)
		sys.stdout.flush()
		for i in range(clipboardtime):
			time.sleep(1)
			sys.stdout.write('\x08 \x08')
			sys.stdout.flush()
#
hash_parser = subparsers.add_parser('hash')
hash_parser.add_argument(
	'saltid',
	metavar='SALT',
	nargs='?')
hash_parser.set_defaults(func=cmd_hash)


#
#
def cmd_list(args, pwh):
	w = maxstringlen(pwh.user_salts.keys()) + 2
	for salt in sorted(pwh.user_salts):
		print salt.ljust(w), pwh.user_salts[salt]['description']
list_parser = subparsers.add_parser('list')
list_parser.set_defaults(func=cmd_list)


#
#
def cmd_forget(args, pwh):
	if args.saltid in pwh.user_salts:
		del pwh.user_salts[args.saltid]
		pwh.save_config()
	else:
		print 'ERROR: Salt \'' + args.saltid + '\' not found'
forget_parser = subparsers.add_parser('forget')
forget_parser.add_argument(
	'saltid',
	metavar='SALT')
forget_parser.set_defaults(func=cmd_forget)


#
#
def cmd_lshashschemes(args, pwh):
	w = maxstringlen(pwh.hashschemes.keys()) + 2
	for sid in sorted(pwh.hashschemes):
		print sid.ljust(w), pwh.hashschemes[sid]['description']
#
lshashschemes_parser = subparsers.add_parser('lshashschemes')
lshashschemes_parser.set_defaults(func=cmd_lshashschemes)


#
#
def cmd_lswordschemes(args, pwh):
	w = maxstringlen(pwh.wordschemes.keys()) + 2
	for sid in sorted(pwh.wordschemes):
		print sid.ljust(w), pwh.wordschemes[sid]['description']
#
lswordschemes_parser = subparsers.add_parser('lswordschemes')
lswordschemes_parser.set_defaults(func=cmd_lswordschemes)


#
#
def cmd_license(args, pwh):
	sys.stdout.write(__loader__.get_data('LICENSE.md'))
license_parser = subparsers.add_parser('license')
license_parser.set_defaults(func=cmd_license)



args = parser.parse_args()

pwh = pwhash.PWHash('.narvi')
args.func(args, pwh)



# pwhash
#   prompt for salt, go to hash sub cmd
#
# pwhash hash SALT
#   if SALT is known:
#     prompt for MASTER
#     run key derivation function
#     compute checksum of key
#     if checksum does not match:
#       back to password prompt
#     convert key bytes to password
#     copy password to clipboard
#   else SALT is unknown:
#     prompt for DESCRIPTION
#     prompt for KDFARGS
#     prompt for WORDIFIER
#     prompt for MASTER
#     prompt for MASTER
#     if not match: restart
#     run key derivation function
#     compute CHECKSUM
#     store DESCRIPTION, SALT, KDF, CHECKSUM
#     convert key bytes to password
#     copy password to clipboard
#
# pwhash list [-l]
#   list known SALTs [with DESCRIPTION]
#
# pwhash info SALT
#   list all info on SALT
#
# pwhash forget SALT
#   remove SALT from cache
#
# pwhash lskdfs [-l]
#   list KDFs
#
# pwhash lswordifiers [-l]
#   list wordifiers
#
# pwhash getglobal
# pwhash setglobal
#
#
# data storage:
#   json-encoded
#   {
#     'modulepaths': [
#     ]
#     'globalsettings' :{
#       'default-hashscheme': string,
#       'default-wordscheme': string,
#       'clipboard-time': number
#     }
#     'salts': {
#        SALT1: {
#          'description': string,
#          'hashscheme': string,
#          'wordscheme': string,
#          'checksum': number
#        },
#        SALT2: {
#          'description': string,
#          'hashscheme': string,
#          'wordscheme': string,
#          'checksum': number
#        }
#      }
#   }
#
#
# KDFs:
#
#  scrypt-16-8-1-512  (relative strength 0)
#  scrypt-20-8-1-512  (10)
#
# wordifiers:
#
#  base64-!@-16-aA1
#  pin-4
#
#
# modules:
#
#  mods/scrypt.py
#  mods/base64.py
#
#  each mod has one export:
#
#   provides = {
#     'hashfunctions' = {
#        KDFNAME: {
#          'f': function(parameters, password, salt)
#        }
#     },
#     'hashschemes' = {
#        'scrypt-16-8-1-512': {
#          'description':  '...',
#          'hashfunction': 'scrypt'
#          'hashparams': {
#            'N':     (1 << 16),
#            'r':     8,
#            'p':     1,
#            'dklen': 512
#          }
#        }
#     },
#     'wordfunctions' = {
#        NAME: {
#          'f': function(parameters, buf)
#        }
#     }
#     'wordschemes': {
#        'base64-16-!@-aA1': {
#          'description':  '...',
#          'wordfunction': 'base64'
#          'wordparams':   {
#            'pwlen':     16
#            'altchars': '!@'
#          }
#        }
#     }
#   }
#




