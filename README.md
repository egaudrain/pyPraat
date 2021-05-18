# pyPraat

Tools to interface calls to [Praat](http://www.fon.hum.uva.nl/praat/) from Python and Matlab.

pyPraat is written for Python 3.7 and has been tested with Matlab R2015b.

The project only contains 2 files at the moment:
- `get_formants.py` / `get_formants.m`: to extract formants from a WAV file. The Python script calls Praat with the appropriate options/scripts, parses the result file and returns the data in JSON, Matlab literal, or Matlab .mat format. The Matlab script calls the Python script and returns the data as a `struct()`.
- `TextGrid.py`: A class to parse Praat's TextGrid files.

## `get_formants`

Extract formants with Praat and parses the output file, then convert optionnally convert to another format.

This function can called from the command line, as Python module, or from Matlab.

From the command line you can specify the following options. See [the Praat documentation](https://www.fon.hum.uva.nl/praat/manual/Sound__To_Formant__burg____.html) for the meaning of the parameters.

```
usage: get_formants.py [-h] [--method {burg}] [--timestep TIME_STEP]
                       [--wlen W_LEN] [--maxfreq MAX_FREQ]
                       [--nformants N_FORMANTS]
                       [--export {none,matlabliteral,matfile,json,jsonfile}]
                       [--exportfile EXPORTFILE]
                       FILE
```

As a Python module, you can use it as follows:

```python
from get_formants import Formants

f = Formants('test.wav', timestep=12.5e-3, wlen=50e-3, maxfreq=10000, nformants=7)

from matplotlib import pyplot as plt
import numpy as np

t = f.data['t']
ff = np.array(f.data['formants'])

plt.figure()
plt.plot(t, ff)
plt.show()
```

From Matlab, call the `get_formants()` function:

```matlab
[dat, r] = get_formants(filename, method, time_step, n_formants, max_freq, w_len, export_method);
```

## ToDo

More recent versions of Matlab are distributed with their own version of Python, and allow direct calls using the `py` object. At the moment we are using `system` calls to deal with the Python code, but it might be more efficient to use the `py` object. However, that might break compatibility with Octave (which, admittedly, we haven't tested so far anyway).
