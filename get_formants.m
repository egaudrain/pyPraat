function [dat, r] = get_formants(filename, method, time_step, n_formants, max_freq, w_len, export_method)
%GET_FORMANTS(FILENAME)
%   Extracts the formants using Praat and parses the output to produce a
%   Matlab structure.
%
%   GET_FORMANTS(FILENAME, METHOD, TIME_STEP, N_FORMANTS, MAX_FREQ, W_LEN, EXPORT_METHOD)
%   - FILENAME is WAV file (or any sound file that can be processed by
%     Praat)
%   - METHOD is the method used by Praat to extract the formants (default
%    'burg'). At the moment, only 'burg' is implemented.
%   - TIME_STEP is the periodicity at which formant estimates are
%     obtained, in seconds (default 0.005). 0 means auto (see Praat).
%   - N_FORMANTS is the number of extracted formants (default, 5).
%   - MAX_FREQ is the maximal formant frequency (in Hertz, default 5500).
%   - W_LEN is the analysis window length used to estimate LPC order that 
%     will be used for formant estimation (in seconds, default 0.025).
%   - EXPORT_METHOD is the method used by the underlying Python script to
%     send the data back to Matlab. The possible values are 'matlabliteral'
%     (default), 'matfile', 'json' and 'jsonfile'. 'matlabliteral' seems to
%     be the fastest for short sounds, but it could be different for longer
%     files.
%
%   The function returns a structure DAT that contains information about
%   the formants, and, optionally, a string that is the output of the
%   python script and who's content depends on EXPORT_METHOD.
%
%   The structure DAT has the following fields:
%   - xmin and xmax: the time range over which the formants were evaluated
%   - x1: the time of the first estimate
%   - dx: the TIME_STEP
%   - nx: the number of formant estimates
%   - maxnFormants: the maximum number of formant estimates at each time
%     step
%   - formants: an array of nx by maxnFormants values containing the
%     formant frequency estimates, in Hertz, or NaN if no formant was found
%   - bandwidths: the bandwidths of the formants in an array of same size
%   - intensity: the intensity of the time segment
%   - t: the time at the time segment
%
%   This function requires Python 2.7 to be installed, and in the path, as 
%   well as Praat (installed at its normal location).

% Generate a temporary sound file 

%pyversion('/home/crouzet-o/anaconda3/envs/python2/bin/python');

p = mfilename('fullpath');
py = fullfile(fileparts(p), 'get_formants.py');

if nargin<2
    method = 'burg';
end

if nargin<3
    time_step = 0.005;
end

if nargin<4
    w_len = 0.05;
end

if nargin<5
    max_freq = 5500;
end

if nargin<6
    n_formants = 5;
end

if nargin<7
    export_method = 'matlabliteral';
end


% get_formants.m acts on a file. Could / Should it be meant to act on a matlab matrix
% / wave structure by providing a sound object as input and copying it on
% temporary disk space?
[s, r] = system(sprintf('python2 "%s" --method "%s" --timestep %f --wlen %f --maxfreq %0d --nformants %0d --export "%s" "%s"', py, method, time_step, w_len, max_freq, n_formants, export_method, absolute_path(filename)));
% Note: Used which(filename) to get an absolute path

r = strtrim(r);

if s~=0
    error(r);
end

switch export_method
    case 'matlabliteral'
        dat = eval(r);
    case 'matfile'
        dat = load(r);
    case 'json'
        dat = matlab.internal.webservices.fromJSON(native2unicode(r, 'utf-8'));
    case 'jsonfile'
        f = fopen(r,'r','n','utf-8');
        r = fread(f,Inf,'*char');
        fclose(f);
        dat = matlab.internal.webservices.fromJSON(r);
end

%=======================================================
function s = absolute_path(filename)

f = java.io.File(filename);
if f.isAbsolute()
    s = filename;
elseif filename(1)=='~'
    h = char(java.lang.System.getProperty('user.home'));
    s = [h, filename(2:end)];
    f = java.io.File(s);
    s = f.getCanonicalPath();
else
    f = java.io.File(pwd(), filename);
    s = f.getCanonicalPath();
end

s = char(s);
