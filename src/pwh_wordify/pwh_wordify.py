
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


def _basic_encoder(pwh, params, keymaterial):
	e = pwh.wordfunctions[params['encoder']]['f']
	ekm = e(pwh, params, keymaterial, True)
	pwlen = params['pwlen']
	pos = 0
	while pos + pwlen <= len(ekm):
		password = ekm[pos:(pos + pwlen)]
		if _is_sufficiently_complex(password, params):
			return password
		pos += 1
	return None


def _base64_encode(pwh, params, keymaterial, isencoder=False):
	if not isencoder: raise ValueError
	ekm = base64.b64encode(keymaterial, params['altchars'])
	# ignore any final padding
	return ekm[:-4]


def _base32_encode(pwh, params, keymaterial, isencoder=False):
	if not isencoder: raise ValueError
	ekm = base64.b32encode(keymaterial)
	# ignore any final padding
	return ekm[:-8]


def _mindex1_encode(pwh, params, keymaterial, isencoder=False):
	if not isencoder: raise ValueError
	import struct
	alphabet = params['alphabet']
	divisor = len(alphabet)
	if divisor > 256:
		raise ValueError()
	limit = 256 - (256 % divisor)
	s = struct.Struct('=B')
	ekm = ''
	pos = 0
	for c in keymaterial:
		b = s.unpack(c)[0]
		pos += 1
		if b < limit:
			ekm += alphabet[b % divisor]
	return ekm


def _mindex4_encode(pwh, params, keymaterial, isencoder=False):
	if not isencoder: raise ValueError
	import struct
	alphabet = params['alphabet']
	radix = len(alphabet)
	if radix > 256:
		raise ValueError
	divisors = [radix ** x for x in range(3, 0, -1)]
	vmax = radix ** 4
	limit = (256 ** 4) - ((256 ** 4) % vmax)
	s = struct.Struct('<I')
	ekm = ''
	pos = 0
	while (pos + 4) < len(keymaterial):
		v = s.unpack_from(keymaterial, pos)[0]
		if v < limit:
			pos += 4
			v = v % vmax
			for d in divisors:
				ekm += alphabet[v // d]
				v = v % d
			ekm += alphabet[v]
		else:
			pos += 1
	return ekm


def _distro(abet, buf):
	d = {}
	for c in abet:
		d[c] = 0
	for c in buf:
		d[c] += 1
	for g in [sorted(d.keys())[x:x+5] for x in xrange(0, len(d), 5)]:
		for c in g:
			print c + ':', d[c], '\t',
		print ''


provides = {
  'wordfunctions': {
    'encoder': {
      'f': _basic_encoder
    },
    'base64': {
      'f': _base64_encode
    },
    'base32': {
      'f': _base32_encode
    },
    'mindex1': {
      'f': _mindex1_encode
    },
    'mindex4': {
      'f': _mindex4_encode
    }
  },
  'wordschemes': {
    'base64-16-!@-aA1': {
      'description': 'base64 alphabet (\'!\' and \'@\' as extra characters), 16 characters long, at least one each of lower case, upper case, and number',
      'wordfunctionid': 'encoder',
      'wordparams': {
        'pwlen': 16,
        'encoder': 'base64',
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
      'wordfunctionid': 'encoder',
      'wordparams': {
        'pwlen': 10,
        'encoder': 'base32'
      }
    },
    'pin-4': {
      'description': '4-digit PIN',
      'wordfunctionid': 'encoder',
      'wordparams': {
        'pwlen': 4,
        'encoder': 'mindex4',
        'alphabet': '0123456789'
      }
    },
    'pin-5': {
      'description': '5-digit PIN',
      'wordfunctionid': 'encoder',
      'wordparams': {
        'pwlen': 5,
        'encoder': 'mindex4',
        'alphabet': '0123456789'
      }
    },
    'pin-6': {
      'description': '6-digit PIN',
      'wordfunctionid': 'encoder',
      'wordparams': {
        'pwlen': 6,
        'encoder': 'mindex4',
        'alphabet': '0123456789'
      }
    }
  }
}


__all__ = ['provides']

