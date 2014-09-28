#!/bin/ksh

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



OUTFILE=scrypt-hash.so

SCRYPTDIR=scrypt-1.1.6
SCRYPTLIBROOT=${SCRYPTDIR}/lib

OBJDIR=obj


set -e
set -x
mkdir ${OBJDIR}
cp config-Darwin.h ${OBJDIR}/config.h
cp ${SCRYPTDIR}/scrypt_platform.h ${OBJDIR}/
cp ${SCRYPTLIBROOT}/util/sysendian.h ${OBJDIR}/
cp ${SCRYPTLIBROOT}/crypto/sha256.h ${OBJDIR}/
cp ${SCRYPTLIBROOT}/crypto/sha256.c ${OBJDIR}/
cp ${SCRYPTLIBROOT}/crypto/crypto_scrypt.h ${OBJDIR}/
cp ${SCRYPTLIBROOT}/crypto/crypto_scrypt-sse.c ${OBJDIR}/

cd ${OBJDIR} && clang -dynamiclib -std=gnu99 -arch i386 -arch x86_64 -O3 -DCONFIG_H_FILE=\"config.h\" -o ${OUTFILE} crypto_scrypt-sse.c sha256.c

