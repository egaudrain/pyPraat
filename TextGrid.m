function x = TextGrid(fname)

p = mfilename('fullpath');
[pathstr, name, ext, versn] = fileparts(p);
p = fullfile(pathstr, 'TextGrid.py');

[s, c] = system(sprintf('python "%s" "%s"', p, fname));
try
    eval(c);
catch ME
    disp(c);
    rethrow(ME);
end
    