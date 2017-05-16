
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
	