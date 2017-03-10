# pyPraat

Tools to interface calls to [Praat](http://www.fon.hum.uva.nl/praat/) from Python and Matlab.

pyPraat is written for Python 2.7 and has been tested with Matlab R2015b.

The project only contains 2 functions at the moment:
- `get_formants`: to extract formants from a WAV file. The Python script calls Praat with the appropriate options/scripts, parses the result file and returns the data in JSON, Matlab literal, or Matlab .mat format. The Matlab script calls the Python script and returns the data as a `struct()`.
- `TextGrid`: A class to parse Praat's TextGrid files.

## ToDo

More recent versions of Matlab are distributed with their own version of Python, and allow direct calls using the `py` object. At the moment we are using `system` calls to deal with the Python code, but it might be more efficient to use the `py` object. However, that might break compatibility with Octave (which, admittedly, we haven't tested so far anyway).
