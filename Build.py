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


import os
import shutil
import zipfile
import stat


class BuildContext(object):
	pass


TheBuild = BuildContext()
TheBuild.sandboxroot = os.path.dirname(os.path.realpath(__file__))
TheBuild.srcroot = os.path.join(TheBuild.sandboxroot, 'src')
TheBuild.objroot = os.path.join(TheBuild.sandboxroot, 'obj')
TheBuild.libcontents = {}
TheBuild.zipcontents = {}


print ''
print 'Sandbox root:', TheBuild.sandboxroot
print 'Source root :', TheBuild.srcroot
print 'Obj root    :', TheBuild.objroot
print ''

if os.path.exists(TheBuild.objroot):
	print 'Removing previous build artifacts...'
	shutil.rmtree(TheBuild.objroot)
os.mkdir(TheBuild.objroot)


for root, dirs, files in os.walk(TheBuild.srcroot):
	break
for d in dirs:
	srcdir = os.path.join(TheBuild.srcroot, d)
	buildscript = os.path.join(srcdir, 'Build.py')
	if os.path.exists(buildscript):
		TheBuild.srcdir = srcdir
		print 'Processing', buildscript[len(TheBuild.sandboxroot)+1:]
		execfile(buildscript)


TheBuild.libzipfile = os.path.join(TheBuild.objroot, 'libzip', 'lib.zip')
print 'Creating', TheBuild.libzipfile[len(TheBuild.sandboxroot)+1:], '...'
os.mkdir(os.path.dirname(TheBuild.libzipfile))
libzip = zipfile.ZipFile(TheBuild.libzipfile, 'w', zipfile.ZIP_DEFLATED)
for k in sorted(TheBuild.libcontents.keys()):
	print '\t' + k
	libzip.write(TheBuild.libcontents[k], k)
libzip.close()
TheBuild.zipcontents['pwhash/lib.zip'] = TheBuild.libzipfile


TheBuild.narvizipfile = os.path.join(TheBuild.objroot, 'narvizip', 'narvi.zip')
print 'Creating', TheBuild.narvizipfile[len(TheBuild.sandboxroot)+1:], '...'
os.mkdir(os.path.dirname(TheBuild.narvizipfile))
narvizip = zipfile.ZipFile(TheBuild.narvizipfile, 'w', zipfile.ZIP_DEFLATED)
for k in sorted(TheBuild.zipcontents.keys()):
	print '\t' + k
	narvizip.write(TheBuild.zipcontents[k], k)
narvizip.close()


TheBuild.narviexe = os.path.join(TheBuild.objroot, 'narvi')
print 'Creating', TheBuild.narviexe[len(TheBuild.sandboxroot)+1:], '...'
narviexe = open(TheBuild.narviexe, 'wb')
narviexe.write('#!/usr/bin/python\n')
shutil.copyfileobj(open(TheBuild.narvizipfile, 'rb'), narviexe)
narviexe.close()
os.chmod(TheBuild.narviexe, stat.S_IRWXU)

