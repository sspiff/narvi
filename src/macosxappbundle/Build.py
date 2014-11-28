
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


@build_step('mac-appbundle-skeleton', [], [])
def build_macappbundleskeleton(build):
	app = {}
	app['bundleroot'] = os.path.join(build.objroot, 'narvi.app.tmp')
	app['contents']   = os.path.join(app['bundleroot'], 'Contents')
	app['macos']      = os.path.join(app['contents'], 'MacOS')
	app['resources']  = os.path.join(app['contents'], 'Resources')
	os.mkdir(app['bundleroot'])
	os.mkdir(app['contents'])
	os.mkdir(app['macos'])
	os.mkdir(app['resources'])
	build.macappbundle = app

@build_step('mac-icns',
	['mac-appbundle-skeleton'],
	['mac-appbundle'])
def build_macicns(build):
	# first, build the iconset
	icnsroot = os.path.join(build.objroot, 'macicns')
	iconset  = os.path.join(icnsroot, 'narvi.iconset')
	os.mkdir(icnsroot)
	os.mkdir(iconset)
	for i in [16, 32, 128, 256, 512]:
		f = 'icon_' + str(i) + 'x' + str(i) + '.png'
		print '\tGenerating', f
		build.export_icon_png(os.path.join(iconset, f), i)
		f = 'icon_' + str(i) + 'x' + str(i) + '@2x.png'
		print '\tGenerating', f
		build.export_icon_png(os.path.join(iconset, f), (i*2))
	# next, create the icns file
	icnsfile = os.path.join(build.macappbundle['resources'], 'narvi.icns')
	cmd = ['iconutil', '-c', 'icns', iconset]
	try:
		subprocess.check_output(cmd, stderr=subprocess.STDOUT)
	except subprocess.CalledProcessError as e:
		import sys
		sys.stderr.write(e.output)
		raise e
	shutil.copy(
		os.path.join(icnsroot, 'narvi.icns'),
		icnsfile)

@build_step('mac-infoplist',
	['mac-appbundle-skeleton'],
	['mac-appbundle'])
def build_macinfoplist(build):
	import json
	plist = json.load(open(
		os.path.join(build.srcdir, 'infoplist.json')))
	plist['CFBundleVersion'] = build.version
	plist['CFBundleShortVersionString'] = build.version
	#
	plistfile = os.path.join(build.macappbundle['contents'], 'Info.plist')
	fd = open(plistfile, 'wb')
	fd.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	fd.write('<!DOCTYPE plist PUBLIC "-//Apple/DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n')
	fd.write('<plist version="1.0">\n')
	fd.write('<dict>\n')
	for k in plist:
		fd.write('\t<key>' + k + '</key>\n')
		fd.write('\t<string>' + plist[k] + '</string>\n')
	fd.write('</dict>\n')
	fd.write('</plist>\n')
	fd.close()

@build_step('mac-appfiles',
	['mac-appbundle-skeleton', 'narviexe'],
	['mac-appbundle'])
def build_macappfiles(build):
	shutil.copy(
		os.path.join(build.srcdir, 'narvi-term'),
		build.macappbundle['macos'])
	shutil.copy(
		build.narviexe,
		build.macappbundle['macos'])

@build_step('mac-appbundle', [], [])
def build_macappbundle(build):
	bundle = os.path.join(build.objroot, 'narvi.app')
	os.rename(build.macappbundle['bundleroot'], bundle)
	build.macappbundle = bundle

@build_step('mac-appbundle-dmg', ['mac-appbundle'], [])
def build_macappbundledmg(build):
	dmgroot = os.path.join(build.objroot, 'mac-dmg')
	os.mkdir(dmgroot)
	dmgapp = os.path.join(dmgroot, 'narvi.app')
	shutil.copytree(build.macappbundle, dmgapp)
	appdirlink = os.path.join(dmgroot, 'Applications')
	os.symlink('/Applications', appdirlink)
	dmgfilename = os.path.join(build.objroot, 'narvi-'+build.version+'.dmg')
	#
	cmd = ['hdiutil', 'create']
	cmd.extend(['-srcfolder', dmgroot])
	cmd.extend([dmgfilename])
	cmd.extend(['-volname', 'narvi-' + build.version])
	try:
		subprocess.check_output(cmd, stderr=subprocess.STDOUT)
	except subprocess.CalledProcessError as e:
		import sys
		sys.stderr.write(e.output)
		raise e


