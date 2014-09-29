
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


re_lcase = re.compile('[a-z]')
re_ucase = re.compile('[A-Z]')
re_num   = re.compile('[0-9]')
def _is_sufficiently_complex(pword):
	global re_lcase
	global re_ucase
	global re_num
	if (
		re_lcase.search(pword) and
		re_ucase.search(pword) and
		re_num.search(pword)):
		return True
	else:
		return False


def _base64_wordify(pwh, params, keymaterial):
	pwchars = base64.b64encode(keymaterial, params['altchars'])
	# ignore any final padding
	pwlen = params['pwlen'] - 2
	keylen = len(pwchars)
	pos = 0
	while pos + pwlen <= keylen:
		password = pwchars[pos:(pos + pwlen)]
		if _is_sufficiently_complex(password):
			return password
		pos += 1
	return None


provides = {
  'wordfunctions': {
    'base64': {
      'f': _base64_wordify
    }
  },
  'wordschemes': {
    'base64-16-!@-aA1': {
      'description': 'base64 alphabet (\'!\' and \'@\' as extra characters), 16 characters long, at least one each of lower case, upper case, and number',
      'wordfunctionid': 'base64',
      'wordparams': {
        'pwlen': 16,
        'altchars': '!@'
      }
    }
  }
}


__all__ = ['provides']

