#!/usr/bin/python3

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
import sys



class DependencyGraphCycle(Exception): pass

class DependencyItem: pass

class DependencyGraph:
	def __init__(self):
		self._graph = {}

	def add_node(self, name, dependson, neededby):
		try:
			o = self._graph[name]
		except KeyError:
			o = DependencyItem()
			self._graph[name] = o
			o.name      = name
			o.dependson = []
		o.dependson.extend(dependson)
		for n in neededby:
			self.add_node(n, [name], [])
		return o

	def visit(self, f, these=None, done={}, seen={}):
		if these is None:
			these = list(self._graph.keys())
		for t in these:
			if t in done:
				continue
			if t in seen:
				raise DependencyGraphCycle(t)
			seen[t] = True
			self.visit(f, self._graph[t].dependson, done, seen)
			f(self._graph[t])
			done[t] = True



TheBuild = DependencyGraph()
TheBuild.sandboxroot = os.path.dirname(os.path.realpath(__file__))
TheBuild.srcroot = os.path.join(TheBuild.sandboxroot, 'src')
TheBuild.objroot = os.path.join(TheBuild.sandboxroot, 'obj')
TheBuild.version = sys.argv[1]
TheBuild.libcontents = {}
TheBuild.zipcontents = {}


print('')
print('Version     :', TheBuild.version)
print('Sandbox root:', TheBuild.sandboxroot)
print('Source root :', TheBuild.srcroot)
print('Obj root    :', TheBuild.objroot)
print('')

if os.path.exists(TheBuild.objroot):
	print('Removing previous build artifacts...')
	shutil.rmtree(TheBuild.objroot)
os.mkdir(TheBuild.objroot)


def build_step(name, dependson, neededby, build=TheBuild):
	def decorator(f):
		srcdir = build.srcdir
		def builder():
			build.srcdir = srcdir
			f(build)
		build.add_node(name, dependson, neededby).build = builder
		return f
	return decorator


for root, dirs, files in os.walk(TheBuild.srcroot):
	break
for d in dirs:
	srcdir = os.path.join(TheBuild.srcroot, d)
	buildscript = os.path.join(srcdir, 'Build.py')
	if os.path.exists(buildscript):
		TheBuild.srcdir = srcdir
		print('Processing', buildscript[len(TheBuild.sandboxroot)+1:])
		exec(compile(open(buildscript, "rb").read(), buildscript, 'exec'))


def build_one(node):
	try:
		b = node.build
	except AttributeError:
		pass
	else:
		print('Building', node.name)
		b()
TheBuild.visit(build_one)


