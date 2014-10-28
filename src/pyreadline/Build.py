
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


pyreadlinesrcfile = 'pyreadline-narvi.zip'
pyreadlinemoddir  = 'pyreadline-narvi/pyreadline/'

zipdir = 'pyreadline/'


objdir = os.path.join(TheBuild.objroot, 'pyreadline')
os.mkdir(objdir)


import zipfile

zippath = os.path.join(TheBuild.srcdir, pyreadlinesrcfile)
zip = zipfile.ZipFile(zippath, 'r')
for i in zip.infolist():
	if not i.filename.startswith(pyreadlinemoddir):
		continue
	if i.filename.startswith(pyreadlinemoddir + 'test/'):
		continue
	objfilename = os.path.join(objdir, i.filename[len(pyreadlinemoddir):])
	if os.sep != '/':
		objfilename = objfilename.replace('/', '\\')
	zipfilename = zipdir + i.filename[len(pyreadlinemoddir):]
	f = zip.open(i)
	if not os.path.isdir(os.path.dirname(objfilename)):
		os.mkdir(os.path.dirname(objfilename))
	shutil.copyfileobj(f, open(objfilename, 'wb'))
	TheBuild.zipcontents[zipfilename] = objfilename

