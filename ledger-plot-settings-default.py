# coding=utf-8

# configurarion

output_size 	= '1000, 600'
output_file 	= 'ledger_plot.png'
time_conversion	= 3600					# means that 3600 seconds are one hour; enter 60 for getting minutes

# info_text and color variables - and boolean for switching between color modes

info_text	 =  'Infotext line 1\n'
info_text	 += 'Infotext line 2\n'

colorize = True

WHITE = '\033[97m'
PURPLE = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
BOLD = '\033[1m'
DIM = '\033[2m'
GREY = '\033[90m'
UNDERLINE = '\033[4m'

# customize the colors here !!!

# normal text
CL_TXT = PURPLE if colorize else ''
# info, error and warning text
CL_INF = BOLD + RED if colorize else ''
# default values
CL_DEF = YELLOW if colorize else ''
# dimmed output
CL_DIM = GREY if colorize else ''
# final output
CL_OUT = BOLD + YELLOW if colorize else ''

# don't change this- it's the ending string for the coloring strings
CL_E = '\033[0m' if colorize else ''