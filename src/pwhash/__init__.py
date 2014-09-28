
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


import os
import imp
import errno
import json
import zipimport
import zipfile
import hashlib
import shutil
import StringIO

from . import plugins


class PWHashError(Exception): pass

class PWHash(object):

	def __init__(self, configdirname='.pwhash'):
		#
		self.config_dir = os.path.expanduser(
			os.path.join('~', configdirname))
		self.config_file = os.path.join(self.config_dir, 'config')
		self.lib_path = os.path.join(self.config_dir, 'lib')
		self.libchecked = False
		#
		self.user_salts = {}
		self.user_settings = {}
		self.load_config()
		#
		self.hashschemes = {}
		self.wordschemes = {}
		self.hashfunctions = {}
		self.wordfunctions = {}
		self.load_plugins()

	def _default_user_config(self):
		return {
			'settings': {
				'default-hashscheme': 'scrypt-18-8-1-512',
				'default-wordscheme': 'base64-16-!@-aA1',
				'clipboard-time': 8,
				'store-checksum': False,
				'lib-version': ''
				},
			'salts': {},
			'hashschemes': {},
			'wordschemes': {}
			}

	def _read_config(self):
		try:
			f = open(self.config_file, 'rb')
		except IOError as e:
			if e.errno == errno.ENOENT:
				return self._default_user_config()
			else:
				raise e
		return json.loads(f.read())

	def _write_config(self, config):
		try:
			f = open(self.config_file, 'wb')
		except IOError as e:
			if e.errno == errno.ENOENT:
				os.mkdir(self.config_dir)
				f = open(self.config_file, 'wb')
			else:
				raise e
		f.write(json.dumps(config,
			sort_keys=True, indent=4, separators=(',', ': ')))
		f.write('\n')

	def load_config(self):
		config = self._read_config()
		self.user_salts = config['salts']
		self.user_settings = config['settings']
		self.user_hashschemes = config['hashschemes']
		self.user_wordschemes = config['wordschemes']

	def save_config(self):
		config = {
			'settings': self.user_settings,
			'salts': self.user_salts,
			'hashschemes': self.user_hashschemes,
			'wordschemes': self.user_wordschemes
			}
		self._write_config(config)

	def _modlist_from_dir(self, path):
		for dirpath, dirnames, filenames in os.walk(path):
			m = []
			m.extend([f[:-3] for f in filenames if f.endswith('.py') and not f.startswith('_')])
			m.extend(dirnames)
			return m

	def _modlist_from_zip(self, zippath, modpath):
		import zipfile
		z = zipfile.ZipFile(zippath)
		m = []
		for f in z.namelist():
			# zipfile seems to always use / as the separator
			if os.sep != '/':
				f = f.replace('/', os.sep)
			dirname, filename = os.path.split(f)
			if (dirname == modpath and
				filename.endswith('.py') and
				not filename.startswith('_')):
				m.append(filename[:-3])
			elif (filename == '__init__.py' and
				os.path.dirname(dirname) == modpath):
				m.append(os.path.basename(dirname))
		return m

	def load_plugin(self, pname):
		try:
			plugmod = __import__(
				'plugins', globals(), locals(),
				[pname], 1)
			plugin = getattr(plugmod, pname)
			p = plugin.provides
		except Exception as e:
			print e
			raise PWHashError(
				'Unable to load plugin \'' + pname + '\'.')
		if 'hashschemes' in p:
			self.hashschemes.update(p['hashschemes'])
		if 'hashfunctions' in p:
			self.hashfunctions.update(p['hashfunctions'])
		if 'wordschemes' in p:
			self.wordschemes.update(p['wordschemes'])
		if 'wordfunctions' in p:
			self.wordfunctions.update(p['wordfunctions'])

	def load_plugins(self):
		self.hashschemes   = {}
		self.hashfunctions = {}
		self.wordschemes   = {}
		self.wordfunctions = {}
		#
		modpath = plugins.__path__[0]
		try:
			if isinstance(__loader__, zipimport.zipimporter):
				zippath = __loader__.archive
		except NameError:
			zippath = None
		#
		if zippath:
			modlist = self._modlist_from_zip(
				zippath, modpath[len(zippath)+1:])
		else:
			modlist = self._modlist_from_dir(modpath)
		#
		for p in modlist:
			self.load_plugin(p)
		#
		self.hashschemes.update(self.user_hashschemes)
		self.wordschemes.update(self.user_wordschemes)

	def _load_libzip(self):
		modpath = __path__[0]
		try:
			if isinstance(__loader__, zipimport.zipimporter):
				zippath = __loader__.archive
		except NameError:
			return None
		#
		libzipname = os.path.join(modpath[len(zippath)+1:], 'lib.zip')
		if os.sep != '/':
			libzipname = libzipname.replace(os.sep, '/')
		return __loader__.get_data(libzipname)

	def install_libs(self):
		if self.libchecked:
			return
		self.libchecked = True
		zipdata = self._load_libzip()
		if not zipdata:
			return
		md5 = hashlib.md5(zipdata).hexdigest()
		if md5 == self.user_settings['lib-version']:
			return
		if not os.path.isfile(self.config_file):
			return
		#
		print 'INFO: installing latest libs'
		shutil.rmtree(self.lib_path, True)
		os.mkdir(self.lib_path)
		z = zipfile.ZipFile(StringIO.StringIO(zipdata))
		z.extractall(self.lib_path)
		self.user_settings['lib-version'] = md5
		self.save_config()

	def generate_password(self, sd, masterpassword):
		self.install_libs()
		salt   = sd['value']
		hashsid = sd['hashschemeid']
		wordsid = sd['wordschemeid']
		# get components
		try:
			hashs   = self.hashschemes[hashsid]
			hashfid = hashs['hashfunctionid']
			hashp   = hashs['hashparams']
		except KeyError:
			raise PWHashError('Hash scheme \'' + hashsid + '\' is not defined.')
		try:
			hashf = self.hashfunctions[hashfid]['f']
		except KeyError:
			raise PWHashError('Hash function \'' + hashfid + '\' not available.')
		try:
			words   = self.wordschemes[wordsid]
			wordfid = words['wordfunctionid']
			wordp   = words['wordparams']
		except KeyError:
			raise PWHashError('Word scheme \'' + wordsid + '\' not defined.')
		try:
			wordf = self.wordfunctions[wordfid]['f']
		except KeyError:
			raise PWHashError('Word function \'' + wordfid + '\' not available.')
		# generate derived key
		derivedkey = hashf(self, hashp, masterpassword, salt)
		# compute checksum
		checksum = self.generate_checksum(derivedkey)
		# convert to word
		password = wordf(self, wordp, derivedkey)
		return (password, checksum)

	def generate_checksum(self, buf):
		cksum = 0
		for b in buf:
			cksum = (cksum + ord(b)) & 0xff
		return cksum


# data
#
# globals:
#  DEFAULT_HASHSCHEME
#  DEFAULT_WORDSCHEME
#  STORE_CHECKSUM
#
# list of SALTs:
#   SALT
#   DESCRIPTION
#   HASHSCHEME
#   WORDSCHEME
#   CHECKSUM
#
# list of HASHSCHEMEs:
#   HASHSCHEME
#   DESCRIPTION
#   FUNCTION
#   PARAMS
#
# list of WORDSCHEMEs:
#   WORDSCHEME
#   DESCRIPTION
#   FUNCTION
#   PARAMS
#
# list of HASHFUNCTIONS:
#   HASHFUNCTION
#   f
#
# list of WORDFUNCTIONS:
#   WORDFUNCTION
#   f
#   

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
# pwhash lshashschemes [-l]
#   list KDFs
#
# pwhash lswordschemes [-l]
#   list wordifiers
#
# pwhash lsglobal
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
#     '  default-wordscheme': string,
#     }
#     'salts': {
#        SALT1: {
#          'value': string,
#          'description': string,
#          'hashschemeid': string,
#          'wordschemeid': string,
#          'checksum': number
#        },
#        SALT2: {
#          'value': string,
#          'description': string,
#          'hashschemeid ': string,
#          'wordschemeid ': string,
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
#          'hashfunctionid': 'scrypt'
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
#          'wordfunctionid': 'base64'
#          'wordparams':   {
#            'pwlen':     16
#            'altchars': '!@'
#          }
#        }
#     }
#   }
#




