
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


@build_step('pyscrypt', [], ['zipcontents'])
def build_pyscrypt(build):
	pyscryptsrcfile = 'pyscrypt-1.6.1.tar.gz'
	pyscryptmoddir  = 'pyscrypt-1.6.1/pyscrypt/'

	zipdir = 'pwhash/plugins/pwh_scrypt/pyscrypt/'

	objdir = os.path.join(build.objroot, 'pyscrypt')
	os.mkdir(objdir)

	import tarfile

	tgzfile = os.path.join(build.srcdir, pyscryptsrcfile)
	tar = tarfile.open(tgzfile, 'r')
	for m in tar.getmembers():
		if not m.name.startswith(pyscryptmoddir):
			continue
		objfilename = os.path.join(objdir, m.name[len(pyscryptmoddir):])
		zipfilename = zipdir + m.name[len(pyscryptmoddir):]
		f = tar.extractfile(m)
		shutil.copyfileobj(f, open(objfilename, 'wb'))
		build.zipcontents[zipfilename] = objfilename


