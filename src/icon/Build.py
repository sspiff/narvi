
import subprocess

iconsvgpath = os.path.join(TheBuild.srcdir, 'icon.svg')

inkscapebin = '/Applications/Inkscape.app/Contents/Resources/bin/inkscape'

def export_icon_png(pngname, width, inkscapebin=inkscapebin, iconsvgpath=iconsvgpath):
	height = width
	cmd = [inkscapebin, iconsvgpath, '--export-area-page']
	cmd.append('--export-png='+pngname)
	cmd.extend(['-w'+str(width), '-h'+str(height)])
	try:
		subprocess.check_output(cmd, stderr=subprocess.STDOUT)
	except subprocess.CalledProcessError as e:
		import sys
		sys.stderr.write(e.output)
		raise e

TheBuild.export_icon_png = export_icon_png

