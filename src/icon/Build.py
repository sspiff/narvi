
import subprocess

iconsvgpath = os.path.join(TheBuild.srcdir, 'icon.svg')

inkscapebin = '/Applications/Inkscape.app/Contents/Resources/bin/inkscape'

def export_icon_png(pngname, width, inkscapebin=inkscapebin, iconsvgpath=iconsvgpath):
	height = width
	cmd = [inkscapebin, iconsvgpath, '--export-area-page']
	cmd.append('--export-png='+pngname)
	cmd.extend(['-w'+str(width), '-h'+str(height)])
	rc = subprocess.call(cmd)
	if rc != 0:
		raise RuntimeError('inkscape export failed')

TheBuild.export_icon_png = export_icon_png

