
# Copyright (c) 2014, Brian Boylston
# All rights reserved.
# 
# Copyright (c) 2013, Magnus Hallin
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


#
# python bindings adapted from:
#
#   http://bitbucket.org/mhallin/py-scrypt
#


import os
import sys
import platform

from ctypes import (cdll,
                    POINTER, pointer,
                    c_char_p,
                    c_size_t, c_double, c_int, c_uint64, c_uint32,
                    create_string_buffer)

_scrypthashlib = None
_crypto_scrypt = None


def _normalized_isa():
	claim = platform.machine().lower()
	if claim in [
		'i386', 'i686', 'x86_64', 'amd64', 'x86', 'x86pc', 'i86pc']:
		return 'x86'
	else:
		return claim


def _address_size():
	if sys.maxsize > 2**32:
		return '64'
	else:
		return '32'


def _construct_libname():
	opsys = platform.system().lower()
	isa   = _normalized_isa()
	bits  = _address_size()
	components = ['scrypthash', opsys, isa]
	if opsys not in ['darwin']:
		components.append(bits)
	if opsys in ['windows']:
		ext = '.dll'
	else:
		ext = '.so'
	return '-'.join(components) + ext


def init(libpath=''):
	global _scrypthashlib
	global _crypto_scrypt
	if _scrypthashlib:
		return
	#
	libname = _construct_libname()
	_scrypthashlib = cdll.LoadLibrary(os.path.join(libpath, libname))
	#
	_crypto_scrypt = _scrypthashlib.crypto_scrypt
	_crypto_scrypt.argtypes = [
		c_char_p,  # const uint8_t *passwd
		c_size_t,  # size_t         passwdlen
		c_char_p,  # const uint8_t *salt
		c_size_t,  # size_t         saltlen
		c_uint64,  # uint64_t       N
		c_uint32,  # uint32_t       r
		c_uint32,  # uint32_t       p
		c_char_p,  # uint8_t       *buf
		c_size_t,  # size_t         buflen
		]
	_crypto_scrypt.restype = c_int


IS_PY2 = sys.version_info < (3, 0, 0, 'final', 0)


class error(Exception):
    def __init__(self, scrypt_code):
        self._scrypt_code = -1
        super(error, self).__init__(scrypt_code)


def _ensure_bytes(data):
    if IS_PY2 and isinstance(data, str):
        return data.encode('utf-8')

    if not IS_PY2 and isinstance(data, str):
        return bytes(data, 'utf-8')

    return data
            

def hash(password, salt, N=1 << 14, r=8, p=1, buflen=64):
    """
    Compute scrypt(password, salt, N, r, p, buflen).

    The parameters r, p, and buflen must satisfy r * p < 2^30 and
    buflen <= (2^32 - 1) * 32. The parameter N must be a power of 2
    greater than 1. N, r and p must all be positive.

    Notes for Python 2:
      - `password` and `salt` must be str instances
      - The result will be a str instance

    Notes for Python 3:
      - `password` and `salt` can be both str and bytes. If they are str
        instances, they wil be encoded with utf-8.
      - The result will be a bytes instance

    Exceptions raised:
      - TypeError on invalid input
      - scrypt.error if scrypt failed
    """

    init()

    outbuf = create_string_buffer(buflen)

    password = _ensure_bytes(password)
    salt = _ensure_bytes(salt)

    if r * p >= (1 << 30) or N <= 1 or (N & (N - 1)) != 0 or p < 1 or r < 1:
        raise error('hash parameters are wrong (r*p should be < 2**30, and N should be a power of two > 1)')

    result = _crypto_scrypt(password, len(password),
                            salt, len(salt),
                            N, r, p,
                            outbuf, buflen)

    if result:
        raise error('could not compute hash')

    return outbuf.raw


__all__ = ['error', 'hash', 'init']

