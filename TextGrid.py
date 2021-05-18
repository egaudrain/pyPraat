#!python
# -*- coding: utf-8 -*-

import re, sys

reIntervals = re.compile(r' +intervals \[[0-9]+\]:')

class TextGrid:
	def __init__(self, fname):
		self.fname = fname
		self.content = open(fname, 'rb').readlines()
		self.parse()
		
	def parse(self):
		# Check the file type
		i, l = self.findLineSW('Object class')
		if i is None or l.strip()!='Object class = "TextGrid"':
			raise Exception('Not a valid TextGrid file')
		
		# Get the size
		i, l = self.findLineSW('size = ')
		if i is None:
			raise Exception("Size can't be determined...'")
		self.size = int(l.strip().replace('size = ', ''))
		
		# Find item blocks
		idx = list()
		for j in range(self.size):
			i, l = self.findLineSW('    item [%d]:' % (j+1), i+1)
			idx.append(i)
		idx.append(len(self.content))
		self.itemRanges = list()
		for j in range(self.size):
			self.itemRanges.append((idx[j]+1, idx[j+1]))
		
		# Find intervals
		self.intervals = list()
		for j in range(self.size):
			self.intervals.append(list())
			i1 = self.itemRanges[j][0]
			i2 = self.itemRanges[j][1]
			while i1<i2:
				l = self.content[i1]
				if reIntervals.match(l) is not None:
					interval = {
						'xmin': float(self.content[i1+1].strip().replace('xmin = ', '')),
						'xmax': float(self.content[i1+2].strip().replace('xmax = ', '')),
						'text': self.content[i1+3].strip().replace('text = ', '').strip('"')
						}
					self.intervals[j].append(interval)
					i1 += 4
				else:
					i1 += 1
	
	def findLineSW(self, line, start=0, end=None):
		if end is None:
			end = len(self.content)
		for i, l in enumerate(self.content[start:end]):
			if l.startswith(line):
				return i+start, l
		return None, None
	
	def matlabDisp(self):
		s = 'x = struct();\n';
		for j in range(self.size):
			if j==0:
				s += 'x.interval(%d) = struct();\n' % (j+1)
			for i in range(len(self.intervals[j])):
				s += 'x.interval(%d).label(%d).x = [%f, %f];\n' % (j+1, i+1, self.intervals[j][i]['xmin'], self.intervals[j][i]['xmax'])
				s += 'x.interval(%d).label(%d).text = \'%s\';\n' % (j+1, i+1, self.intervals[j][i]['text'])
		print(s)

#==============================================

#~ if __name__=='__main__':
	#~ tg = TextGrid(r'D:\Sounds\for Matt\Cc_01_l1.TextGrid')
	#~ tg.matlabDisp()

tg = TextGrid(sys.argv[1])
tg.matlabDisp()