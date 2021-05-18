#!/usr/bin/env python
# -*- coding: utf-8 -*-

#==============================================================================
# Formant extraction through Praat.
#
# If used from command line, see --help to see usage.
#
# If used as a library, the call() function creates the formant file. The Formant class
# parses the formant file and can export it in various format.
#-------------------------------------------------------------------------------
# E. Gaudrain <etienne.gaudrain@cnrs.fr> - 2017-02-21
#
# 2021-05-18: Added module interface.
#
# Copyright CNRS (FR), UMCG (NL) and the authors.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#================================================================================


import subprocess
import argparse
import platform
import os.path
import re
import numpy

# Added options: wlength, maxfreq, nformants

#=================================================

praat_script = """
	form Get formants
		sentence filename
		sentence filename_formant
		word method
		positive time_step 0.005
        positive n_formants 5
        positive max_freq 5500
        positive w_len 0.025
	endform
	Read from file... 'filename$'
	object_name$ = selected$("Sound")
	To Formant ('method$')... time_step n_formants max_freq w_len 50
	#To Formant ('method$')... time_step 5 5500 0.025 50
	#Track... 3 550 1650 2750 3850 4950 1 1 1
	Write to text file... 'filename_formant$'
	select all
	Remove
	clearinfo
	"""

#=================================================

p = platform.system()
if p=='Darwin':
	praat_path = '/Applications/Praat.app/Contents/MacOS/Praat'
elif p=='Windows':
	praat_path = 'C:\\Progam Files\\Praat.exe'
elif p=='Linux':
	praat_path = '/usr/bin/praat'
else:
	raise ValueError("No implementation for this platform (%s). Don't know where to find Praat..." % p)

if not os.path.exists(praat_path):
	raise ValueError("Could not find Praat in %s..." % praat_path)

#=================================================

parser = argparse.ArgumentParser(description='Compute formants for a WAV file using Praat.', epilog='Written by Etienne Gaudrain <etienne.gaudrain@cnrs.fr>\nCopyright 2017 CNRS (FR), UMCG (NL)', formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('filename', metavar='FILE', help="The sound file to process.")
parser.add_argument('--method', help="The method used to extract the formants (see Praat).", default='burg', choices=['burg'])
parser.add_argument('--timestep', metavar='TIME_STEP', help="The time interval between two consecutive formant estimates (in seconds, default: 0.00625).", default=0.00625, type=float)
parser.add_argument('--wlen', metavar='W_LEN', help="The analysis window length (in seconds, default: 0.025).", default=0.025, type=float)
parser.add_argument('--maxfreq', metavar='MAX_FREQ', help="The maximal frequency (Hz, default: 5500).", default=5500, type=float)
parser.add_argument('--nformants', metavar='N_FORMANTS', help="The number of resulting formants (default: 5).", default=5, type=float)
parser.add_argument('--export', help="Format in which the data should be exported (default 'none'). If a file format is given, an output filename may also be provided or the progam will generate one and will return it.", default='none', choices=['none', 'matlabliteral', 'matfile', 'json', 'jsonfile'])
parser.add_argument('--exportfile', help="File to which the data will be exported, if the export format is a file.")

DEFAULT_VALUES = vars(parser.parse_args(['']))

def call(args):

	if isinstance(args, argparse.Namespace):
		args = vars(args)

	if 'filename' not in args:
		raise ValueError('You need to provide a filename...')

	root, ext = os.path.splitext(args['filename'])
	filename_formant = root + '.formant'

	praat_script_name = __file__.replace('.py', '.praat')

	open(praat_script_name, 'w').write(praat_script)

	cmd = [praat_path, '--run', praat_script_name, args['filename'], filename_formant, args['method'], str(args['timestep']), str(args['nformants']), str(args['maxfreq']), str(args['wlen'])]

	#print(subprocess.list2cmdline(cmd))

	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = p.communicate()
	return filename_formant, p.returncode, stdout, stderr


#=================================================

RE_TYPE = type(re.compile(''))

class Formants:
	"""A class to represent and import formant information for a sound file."""
	def __init__(self, wav_filename=None, **kwargs):

        #self.test = None
		self.f = None
		self.i = -1 # Current line index
		self.data = None

		if wav_filename is not None:
			self.from_wav_file(wav_filename, **kwargs)

	def from_praat_text(self, filename):
		"""Opens and parses a Praat Text file containing formant information. The data is
		then available in self.data."""

		self.f = [x.strip() for x in open(filename, 'r')]
		self.n = len(self.f) # Size of file
		self.i = -1

		if self.f[0] != 'File type = "ooTextFile"':
			raise ValueError("The file isn't a valid Praat Text file (header: '%s')" % self.f[0])
		if self.f[1] != 'Object class = "Formant 2"':
			raise ValueError("The file isn't a valid Praat Formant 2 file (header: '%s')" % self.f[0])

		self.i = 2

		re_ = dict()
		for keyword in ['xmin', 'xmax', 'nx', 'dx', 'x1', 'maxnFormants', 'intensity', 'frequency', 'bandwidth', 'nFormants']:
			re_[keyword] = re.compile(r'%s\s*=\s*([0-9]+(?:\.[0-9]+)?(?:e[+-]?[0-9]+)?)' % keyword)
		re_['frames_array'] = re.compile(r'frames\s*\[\s*\]:')
		re_['frames'] = re.compile(r'frames\s*\[([0-9]+)\]:')
		re_['formant_array'] = re.compile(r'formant\s*\[\s*\]:')
		re_['formant'] = re.compile(r'formant\s*\[([0-9]+)\]:')

		#--------
		self.data = dict()
		for k in ['xmin', 'xmax', 'nx', 'dx', 'x1', 'maxnFormants']:
			self._find_line(re_[k])
			self.data[k] = float(self.last_match.group(1))
		self.data['nx'] = int(self.data['nx'])
		self.data['maxnFormants'] = int(self.data['maxnFormants'])

		self.data['t'] = list()
		self.data['formants'] = list()
		self.data['bandwidths'] = list()
		self.data['intensity'] = list()

		self._find_line(re_['frames_array'])
		while self._find_line(re_['frames']):
			frame = int(self.last_match.group(1))-1
			#print("Frame:", frame, 'on line', self.i)
			self.data['t'].append(self.data['x1']+frame*self.data['dx'])

			self._find_line(re_['intensity'])
			self.data['intensity'].append(float(self.last_match.group(1)))

			i_frame = self.i

			if self._find_line(re_['frames'], self.i+1):
				next_frame = self.i
			else:
				next_frame = self.n
			#print("  Next frame ->", next_frame)

			self.i = i_frame
			self._find_line(re_['formant_array'])
            #print("  Formant [] on line", self.i)
			formants = [numpy.nan]*self.data['maxnFormants']  # Should be the number of requested formants
			bandwidths = [numpy.nan]*self.data['maxnFormants']  # Should be the number of requested formants
			while self._find_line(re_['formant']):
				formant_i = int(self.last_match.group(1))-1

				#print(('    formant [%d] on line' % formant_i), self.i)

				if self.i > next_frame:
					self.i = next_frame
					break

				self._find_line(re_['frequency'])
				frq = float(self.last_match.group(1))
				formants[formant_i] = frq

				#print("    frequency on line", self.i)

				self._find_line(re_['bandwidth'])
				bw = float(self.last_match.group(1))
				bandwidths[formant_i] = bw

				#print("    bandwidth on line", self.i)

			self.data['formants'].append(formants)
			self.data['bandwidths'].append(bandwidths)


	def _find_line(self, pattern, i=None):
		"""A helper function to find a line in a text file."""

		if i is None:
			i = self.i

		if isinstance(pattern, RE_TYPE):
			for k in range(i,self.n):
				self.last_match = pattern.match(self.f[k])
				if self.last_match is not None:
					self.i = k
					return self.f[k]

		elif isinstance(pattern, str):
			for k in range(i,self.n):
				if self.f[k].startswith(pattern):
					self.i = k
					return self.f[k]

		return False


	def to_matlab_literal(self):
		"""Export to Matlab literal (string) that can be interpreted with eval()."""
		if self.data is None:
			raise ValueError("Trying to export an empty formant data set. Call an import method first (e.g. from_praat_text).")

		s = list()
		for k,v in self.data.items():
			f = ["'%s'" % k]
			f.append(self._list_to_matlab_string(v))
			s.extend(f)

		return "struct("+(",".join(s))+")"

	def _list_to_matlab_string(self, a):
		if not self._is_iterable(a):
			return str(a)

		if self._is_iterable(a[0]):
			# We're assuming only dimension 2 table, if there is more depth, it will produce unexpected results
			return "["+(";".join([",".join([str(y) for y in x]) for x in a]))+"]"
		else:
			return "["+(",".join([str(x) for x in a]))+"]"

	def _is_iterable(self, a):
		try:
			iter(a)
			return True
		except Exception:
			return False

	def to_matlab_mat(self, mat_filename):
		"""Export to Matlab MAT file."""
		import scipy.io
		scipy.io.savemat(mat_filename, self.data, do_compression=True)

	def from_wav_file(self, wav_filename, **kwargs):

		args = kwargs
		args['filename'] = wav_filename

		for k in DEFAULT_VALUES:
			if k not in args:
				args[k] = DEFAULT_VALUES[k]

		filename_formant, c, o, e = call(args)

		self.from_praat_text(filename_formant)



#=================================================

if __name__=='__main__':

	args = parser.parse_args()
	filename_formant, c, o, e = call(args)

	if c!=0:
		raise Exception("Formant extraction failed with message:\n"+e)

	if args.export is None or args.export=='none':
		print(filename_formant)
	else:
		f = Formants()
		f.from_praat_text(filename_formant)

		if args.export == 'matlabliteral':
			print((f.to_matlab_literal()))
		elif args.export == 'matfile':
			if args.exportfile is None:
				args.exportfile = filename_formant + '.mat'
			f.to_matlab_mat(args.exportfile)
			print((args.exportfile))
		elif args.export == 'json':
			import json
			print((json.dumps(f.data)))
		elif args.export == 'jsonfile':
			import json
			if args.exportfile is None:
				args.exportfile = filename_formant + '.json'
			json.dump(f.data, open(args.exportfile, 'wb'))
			print((args.exportfile))
