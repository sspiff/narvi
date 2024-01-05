
import subprocess

iconsvgpath = os.path.join(TheBuild.srcdir, 'icon.svg')

inkscapebin = '/Applications/Inkscape.app/Contents/MacOS/inkscape'

def export_icon_png(pngname, width, inkscapebin=inkscapebin, iconsvgpath=iconsvgpath):
	height = width
	cmd = [inkscapebin, iconsvgpath, '--export-area-page']
	cmd.append('--export-type=png')
	cmd.append('--export-filename=-')
	cmd.append('--export-width='+str(width))
	cmd.append('--export-height='+str(height))
	try:
		p = subprocess.run(cmd, check=True, capture_output=True)
		with open(pngname, 'wb') as f:
			f.write(p.stdout)
	except subprocess.CalledProcessError as e:
		import sys
		sys.stderr.write(e.output.decode())
		raise e

TheBuild.export_icon_png = export_icon_png

