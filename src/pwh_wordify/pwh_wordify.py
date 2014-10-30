
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


import re
import base64


def _complexity_score(pword, tests):
	score = 0
	for t in tests:
		if re.search(t['regex'], pword):
			score += t['value']
	return score


def _is_sufficiently_complex(pword, params):
	try:
		c = params['complexity']
	except KeyError:
		return True
	if _complexity_score(pword, c['tests']) < c['minimumscore']:
		return False
	else:
		return True


def _base64_wordify(pwh, params, keymaterial):
	pwchars = base64.b64encode(keymaterial, params['altchars'])
	# ignore any final padding
	keylen = len(pwchars) - 2
	pwlen = params['pwlen']
	pos = 0
	while pos + pwlen <= keylen:
		password = pwchars[pos:(pos + pwlen)]
		if _is_sufficiently_complex(password, params):
			return password
		pos += 1
	return None


def _base32_wordify_simple(pwh, params, keymaterial):
	pwchars = base64.b32encode(keymaterial)
	password = pwchars[:params['pwlen']]
	return password


def _mindex_wordify(pwh, params, keymaterial):
	import struct
	alphabet = params['alphabet']
	divisor = len(alphabet)
	if divisor > 256:
		raise ValueError()
	limit = 256 - (256 % divisor)
	pwlen = params['pwlen']
	password = ''
	pos = 0
	while pwlen > len(password):
		b = struct.unpack_from('=B', keymaterial, pos)[0]
		pos += 1
		if b < limit:
			password += alphabet[b % divisor]
	return password[:pwlen]


provides = {
  'wordfunctions': {
    'base64': {
      'f': _base64_wordify
    },
    'base32simple': {
      'f': _base32_wordify_simple
    },
    'mindex': {
      'f': _mindex_wordify
    }
  },
  'wordschemes': {
    'base64-16-!@-aA1': {
      'description': 'base64 alphabet (\'!\' and \'@\' as extra characters), 16 characters long, at least one each of lower case, upper case, and number',
      'wordfunctionid': 'base64',
      'wordparams': {
        'pwlen': 16,
        'altchars': '!@',
        'complexity': {
          'minimumscore': 3,
          'tests': [
            {'regex': '[a-z]', 'value': 1},
            {'regex': '[A-Z]', 'value': 1},
            {'regex': '[0-9]', 'value': 1}
          ]
        }
      }
    },
    'base32-10': {
      'description': 'base32 alphabet, 10 characters long, good for security question answers with symbol restrictions',
      'wordfunctionid': 'base32simple',
      'wordparams': {
        'pwlen': 10
      }
    },
    'pin-4': {
      'description': '4-digit PIN',
      'wordfunctionid': 'mindex',
      'wordparams': {
        'pwlen': 4,
        'alphabet': '0123456789'
      }
    },
    'pin-6': {
      'description': '6-digit PIN',
      'wordfunctionid': 'mindex',
      'wordparams': {
        'pwlen': 6,
        'alphabet': '0123456789'
      }
    }
  }
}


__all__ = ['provides']

