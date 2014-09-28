
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

def _scrypt_hash(pwh, params, pw, salt):
	try:
		from . import scrypthash
		scrypthash.init(pwh.lib_path)
	except Exception as e:
		print e
		print "INFO: using pure Python scrypt"
		from . import pyscrypt
		hashbytes = pyscrypt.hash(
			password = pw,
			salt     = salt,
			N        = params['N'],
			r        = params['r'],
			p        = params['p'],
			dkLen    = params['dklen'])
	else:
		hashbytes = scrypthash.hash(
			password = pw,
			salt     = salt,
			N        = params['N'],
			r        = params['r'],
			p        = params['p'],
			buflen   = params['dklen'])
	return hashbytes


provides = {
  'hashfunctions': {
    'scrypt': {
      'f': _scrypt_hash
    }
  },
  'hashschemes': {
    'scrypt-14-8-1-512': {
      'description': 'scrypt hash with N=2^14, r=8, p=1, 512-byte hash',
      'hashfunctionid': 'scrypt',
      'hashparams': {
        'N':     (1 << 14),
        'r':     8,
        'p':     1,
        'dklen': 512
      }
    },
    'scrypt-16-8-1-512': {
      'description': 'scrypt hash with N=2^16, r=8, p=1, 512-byte hash',
      'hashfunctionid': 'scrypt',
      'hashparams': {
        'N':     (1 << 16),
        'r':     8,
        'p':     1,
        'dklen': 512
      }
    },
    'scrypt-18-8-1-512': {
      'description': 'scrypt hash with N=2^18, r=8, p=1, 512-byte hash',
      'hashfunctionid': 'scrypt',
      'hashparams': {
        'N':     (1 << 18),
        'r':     8,
        'p':     1,
        'dklen': 512
      }
    },
    'scrypt-20-8-1-512': {
      'description': 'scrypt hash with N=2^20, r=8, p=1, 512-byte hash',
      'hashfunctionid': 'scrypt',
      'hashparams': {
        'N':     (1 << 20),
        'r':     8,
        'p':     1,
        'dklen': 512
      }
    },
    'scrypt-22-8-1-512': {
      'description': 'scrypt hash with N=2^22, r=8, p=1, 512-byte hash',
      'hashfunctionid': 'scrypt',
      'hashparams': {
        'N':     (1 << 22),
        'r':     8,
        'p':     1,
        'dklen': 512
      }
    }
  }
}

__all__ = ['provides']

