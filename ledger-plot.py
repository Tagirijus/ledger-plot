# coding=utf-8

import os, sys, datetime, re, imp


### ### ###
### ### ### load configurarion file for variables
### ### ###

# !!!!! SET YOU INDIVIDUAL SETTINGS FILE HERE
# !!!!! IT MUST BE SET UP LIKE THE 'ledger-plot-settings-default.py' FILE
####
###
#

SETTINGS_FILE = 'ledger-plot-settings.py'

#
###
####
# !!!!!
# !!!!!

# get the actual path to the python script
path_to_project = os.path.dirname(os.path.realpath(__file__))

# check if user set an individual settings file, or load default otherwise

if os.path.isfile(path_to_project + '/' + SETTINGS_FILE):
	configuration = imp.load_source('ledger-plot-settings', path_to_project + '/' + SETTINGS_FILE)
else:
	if os.path.isfile(path_to_project + '/ledger-plot-settings-default.py'):
		configuration = imp.load_source('ledger-plot-settings', path_to_project + '/ledger-plot-settings-default.py')
	else:
		print 'No settings file found.'
		exit()



# getting the variables from the settings file - don't change the values here!

debug_output 	= False

output_size 	= configuration.output_size
output_file 	= configuration.output_file
time_conversion	= configuration.time_conversion

info_text	 =  configuration.info_text

colorize = configuration.colorize

CL_TXT = configuration.CL_TXT
CL_INF = configuration.CL_INF
CL_DEF = configuration.CL_DEF
CL_DIM = configuration.CL_DIM
CL_OUT = configuration.CL_OUT
CL_E = configuration.CL_E

### ### ###
### ### ### load configurarion file for variables - END
### ### ###


# color info_text
info_text = CL_INF + info_text + CL_E



# get ledger_file
# check arguments and environment variable 'LEDGER_FILE_PATH' for ledger file
arguments = sys.argv
# no arguments? check environment variable
if len(arguments) < 2:
	try:
		ledger_file = os.environ['LEDGER_FILE_PATH'] + '/ledger.journal'
	except Exception:
		# nothing set, quit programm
		print CL_INF + 'No arguments given and environment variable LEDGER_FILE_PATH is not set.' + CL_E
		exit()
else:
	# using the argument as the file
	ledger_file = arguments[1]

# check if it exists and if it's a real file
if os.path.exists(ledger_file):
	if not os.path.isfile(ledger_file):
		print CL_INF + 'Given \'ledger file\' is not a file.' + CL_E
		exit()
	else:
		# ... and check if it is a time journal
		f = open(ledger_file, 'r')
		journal_type = f.read()
		f.close()

		# check if a time journal pattern exists anywhere in the journal
		pattern = re.compile('i [0-9]{4}\/[0-9]{2}\/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}')
		if pattern.match(journal_type):
			is_time_journal = True
		else:
			# or check if at least a "; time" comment exists
			if "; time" in journal_type:
				is_time_journal = True
			else:
				is_time_journal = False






# functions and classes
#

def end(s):
	# exits the programm, if s is a dot - used in the functions of the ledger_class
	if s == '.':
		print
		exit()

def add_month(date, month):
	# returns new datetime with months added
	year_add = int(month / 12)
	month_add = int(month % 12)
	if date.month + month_add > 12:
		year_add += 1
		month_add -= 12
	return datetime.datetime(date.year+year_add, date.month+month_add, date.day)

def add_year(date, year):
	# returns new datetime with years added
	return datetime.datetime(date.year+year, date.month, date.day)

def diff_month(d1, d2):
	# return integer, wich represents the difference months
	return (d2.year - d1.year)*12 + d2.month - d1.month

def diff_year(d1, d2):
	# return integer, wich represents the difference years
	return d2.year - d1.year



class plot_class(object):
	def __init__(self):
		# some inits of rsome variables used later
		self.style		= 'lines'
		self.label		= False
		self.autozero	= False
		self.total		= '-J'
		self.count		= False
		self.rate		= '%Y-%m-%d'
		self.fmt		= '%Y/%m/%d'
		self.start		= '1900/01/01'
		self.ende		= '9999/12/31'
		self.span 		= '-d "d>=[' + self.start + '] and d<=[' + self.ende + ']"'
		self.frequency	= ''
		self.accounts	= []
		self.accnames	= []
		self.invert		= []


	def get_array(self, ledger_file, account):
		# generates an array from the ledger output (every line is an array entry)

		# check if 'par:' exists for manual parameter adding
		if 'par:' in account:
			acc = account[account.find(' par:')+5:]
		# check if excluding accounts exists
		elif not 'par:' in account and 'not:' in account:
			# get exclude accounts
			exc = account[account.find(' not:')+5:].split(',')
			# remove possible spaces at beginning or end of each account name and put it in ""
			exc = ['"' + x.strip(' ') + '"' for x in exc]
			# make account (with 'nots') parameter string in ""
			acc = '"' + account[0: account.find(' not:') ] + '" and not ' + ' and not '.join(exc)
		# otherwise ...
		else:
			# make account parameter string in ""
			acc = '"' + account + '"'


		out = []

		# is it a time journal?
		if is_time_journal:
			time_base = '--base'
		else:
			time_base = ''

		# check if mode is "count entries" or normal like "standard ledger analyze output"
		if self.count:
			# get the real first and the last date of the ledger journal and its account
			tmp_led = os.popen( 'ledger -f ' + ledger_file + ' -p "from ' + self.start + ' to ' + self.ende + '" -J r ' + acc).read().splitlines()
			if len(tmp_led) > 1:
				real_start = tmp_led[0].split(' ')[0].replace('-', '/')
				real_ende  = tmp_led[len(tmp_led)-1].split(' ')[0].replace('-', '/')
			else:
				return out

			# check if rate is for days, months or years
			# days
			if self.rate == '%Y-%m-%d':
				# rate is for days, cycle through ALL days from start to end
				ds = datetime.datetime.strptime( real_start, self.fmt)
				de = datetime.datetime.strptime( real_ende, self.fmt)
				diff = (de-ds).days
				# real_start as datetime for temp usage in for loop
				tmp_date = datetime.datetime.strptime( real_start, self.fmt )
				for x in xrange(0,diff+1):
					# getting actual date in cycle
					this_date = (tmp_date + datetime.timedelta(days=x)).strftime(self.fmt)
					# getting count from ledger output
					tmp_out = self.sum_counts( os.popen( 'ledger -f ' + ledger_file + ' ' + time_base + ' -p "' + this_date + '" --count accounts ' + acc).read().splitlines() )
					# check if output is empty or not
					if tmp_out == '' and self.autozero:
						out.append( datetime.datetime.strptime( this_date, self.fmt ).strftime( self.rate ) + ' 0' )
					elif tmp_out:
						out.append( datetime.datetime.strptime( this_date, self.fmt ).strftime( self.rate ) + ' ' + tmp_out.split(' ')[0] )
			# months
			elif self.rate == '%Y-%m':
				# correct real dates
				real_start = real_start[0:7]
				real_ende = real_ende[0:7]
				# rate is for days, cycle through ALL days from start to end
				ds = datetime.datetime.strptime( real_start, self.fmt)
				de = datetime.datetime.strptime( real_ende, self.fmt)
				diff = diff_month(ds, de)
				# real_start as datetime for temp usage in for loop
				tmp_date = datetime.datetime.strptime( real_start, self.fmt )
				for x in xrange(0,diff+1):
					# getting actual date in cycle
					this_date = add_month(tmp_date,x).strftime(self.fmt)
					# getting count from ledger output
					tmp_out = self.sum_counts( os.popen( 'ledger -f ' + ledger_file + ' ' + time_base + ' -p "' + this_date + '" --count accounts ' + acc).read().splitlines() )
					# check if output is empty or not
					if tmp_out == '' and self.autozero:
						out.append( datetime.datetime.strptime( this_date, self.fmt ).strftime( self.rate ) + ' 0' )
					elif tmp_out:
						out.append( datetime.datetime.strptime( this_date, self.fmt ).strftime( self.rate ) + ' ' + tmp_out.split(' ')[0] )
			# years
			elif self.rate == '%Y':
				# correct real dates
				real_start = real_start[0:4]
				real_ende = real_ende[0:4]
				# rate is for days, cycle through ALL days from start to end
				ds = datetime.datetime.strptime( real_start, self.fmt)
				de = datetime.datetime.strptime( real_ende, self.fmt)
				diff = diff_year(ds, de)
				# real_start as datetime for temp usage in for loop
				tmp_date = datetime.datetime.strptime( real_start, self.fmt )
				for x in xrange(0,diff+1):
					# getting actual date in cycle
					this_date = add_year(tmp_date,x).strftime(self.fmt)
					# getting count from ledger output
					tmp_out = self.sum_counts( os.popen( 'ledger -f ' + ledger_file + ' ' + time_base + ' -p "' + this_date + '" --count accounts ' + acc).read().splitlines() )
					# check if output is empty or not
					if tmp_out == '' and self.autozero:
						out.append( datetime.datetime.strptime( this_date, self.fmt ).strftime( self.rate ) + ' 0' )
					elif tmp_out:
						out.append( datetime.datetime.strptime( this_date, self.fmt ).strftime( self.rate ) + ' ' + tmp_out.split(' ')[0] )
		else:
			out = self.fill_dates( os.popen('ledger -f ' + ledger_file + ' ' + time_base + ' ' + self.frequency + ' ' + self.span + ' ' + self.total + ' r ' + acc).read().splitlines() )

		if is_time_journal:
			out = self.time_convert(out)

		if debug_output:
			print 'DEBUG:', out
			print
			print 'DEBUG:', self.sum_same(out)
		return self.sum_same(out)


	def time_convert(self, in_array):
		# returns the array with converted time
		out = []
		for x in in_array:
			out.append( x.split(' ')[0] + ' ' + str( float(x.split(' ')[1]) / time_conversion ) )

		return out


	def sum_counts(self, in_array):
		# returns a string
		out = ''

		# cycle through array and add first value
		val = 0
		for x in in_array:
			val += int(x.split(' ')[0])

		# prepare output
		if len(in_array) > 0:
			out = str(val) + ' -'

		return out


	def sum_same(self, in_array):
		# returns an array
		out = []

		# sums values on same date
		amount = 0
		for y, x in enumerate(in_array):
			if y > 0:
				# the actual date is the same as the last
				if last == x.split(' ')[0]:
					# add its amount to the last ones, when self.total is '-j'
					if self.total == '-j':
						amount += float(x.split(' ')[1])
					# or the amount is the actual amount, since self.total '-J' shows the total already
					elif self.total == '-J':
						amount = float(x.split(' ')[1])
				else:
					# its a new date, put last date + amount into the output array
					out.append( last + ' ' + str(amount) )
					# and reasign / reset 'last' and 'amount'
					last = x.split(' ')[0]
					amount = float(x.split(' ')[1])
			else:
				# add the first line into the temp variables 'last' (date) and 'amount' (value)
				last = x.split(' ')[0]
				amount += float(x.split(' ')[1])
		if len(in_array) > 0:
			out.append( last + ' ' + str(amount) )

		return out


	def fill_dates(self, in_array):
		# generates dates between the start and end date and returns new array with original and filled data

		# cycle through the entries of the array
		out = []

		# cycling through days
		if self.frequency == '':
			for x in xrange(0, len(in_array) ):
				if x > 0 and self.autozero and self.total == '-j':
					ds = datetime.datetime.strptime( in_array[x-1].split(' ')[0], self.rate)
					de = datetime.datetime.strptime( in_array[x].split(' ')[0], self.rate)
					diff = (de-ds).days
					for y in xrange(0,diff):
						out.append( (ds + datetime.timedelta(days=y)).strftime(self.rate + ' 0') )
				out.append( in_array[x] )

		# cycling through months
		elif self.frequency == '-M':
			for x in xrange(0, len(in_array) ):
				if x > 0 and self.autozero and self.total == '-j':
					ds = datetime.datetime.strptime( in_array[x-1].split(' ')[0], self.rate)
					de = datetime.datetime.strptime( in_array[x].split(' ')[0], self.rate)
					diff = diff_month(ds, de)
					for y in xrange(0,diff):
						out.append( add_month(ds, y).strftime(self.rate + ' 0') )
				out.append( in_array[x] )

		# cycling through years
		elif self.frequency == '-Y':
			for x in xrange(0, len(in_array) ):
				if x > 0 and self.autozero and self.total == '-j':
					ds = datetime.datetime.strptime( in_array[x-1].split(' ')[0], self.rate)
					de = datetime.datetime.strptime( in_array[x].split(' ')[0], self.rate)
					diff = diff_year(ds, de)
					for y in xrange(0,diff):
						out.append( add_year(ds, y).strftime(self.rate + ' 0') )
				out.append( in_array[x] )

		return out


	def chose_style(self):
		# print info_text
		print info_text

		correct = False
		while not correct:
			print CL_TXT + '(1) Lines' + CL_E
			print CL_TXT + '(2) Linespoints' + CL_E
			print CL_TXT + '(3) Boxes' + CL_E
			print CL_TXT + '(4) Boxes + Label' + CL_E
			print CL_TXT + '(5) Linespoints (Autozero)' + CL_E
			print CL_TXT + '(6) Boxes (Autozero)' + CL_E
			print CL_TXT + '(7) Boxes (Autozero) + Label' + CL_E
			user = raw_input(CL_TXT + 'Style [' + CL_DEF + '1' + CL_TXT + ']: ' + CL_E)
			end(user)
			if not user:
				user = 1
				correct = True
			else:
				try:
					user = int(user)
					correct = True
				except Exception, e:
					print CL_INF + 'Please enter a valid option.' + CL_E
			print

		if user == 2:
			self.style = 'linespoints'
		elif user == 3:
			self.style = 'boxes'
		elif user == 4:
			self.style = 'boxes'
			self.label = True
		elif user == 5:
			self.style = 'linespoints'
			self.autozero = True
		elif user == 6:
			self.style = 'boxes'
			self.autozero = True
		elif user == 7:
			self.style = 'boxes'
			self.autozero = True
			self.label = True

		self.chose_count()


	def chose_count(self):
		user = raw_input(CL_TXT + 'Count entries? [' + CL_DEF + 'no' + CL_TXT + ']: ' + CL_E)
		end(user)

		print

		if not user:
			user = 'no'

		if not user == 'no':
			self.count = True
			user = raw_input(CL_TXT + 'Rate: (y)ear, (m)onth or (d)ay? [' + CL_DEF + 'day' + CL_TXT + ']: ' + CL_E)
			end(user)
			if user.lower() == 'year' or user.lower() == 'y':
				self.rate = '%Y'
				self.fmt = '%Y'
				self.start = self.start[0:4]
				self.ende = self.ende[0:4]
			elif user.lower() == 'month' or user.lower() == 'm':
				self.rate = '%Y-%m'
				self.fmt = '%Y/%m'
				self.start = self.start[0:7]
				self.ende = self.ende[0:7]
		else:
			user = raw_input(CL_TXT + 'Rate: (y)ear, (m)onth or (n)ormal? [' + CL_DEF + 'normal' + CL_TXT + ']: ' + CL_E)
			end(user)
			if user.lower() == 'year' or user.lower() == 'y':
				self.start = self.start[0:4]
				self.ende = self.ende[0:4]
				self.frequency = '-Y'
			elif user.lower() == 'month' or user.lower() == 'm':
				self.start = self.start[0:7]
				self.ende = self.ende[0:7]
				self.frequency = '-M'

		print
		self.chose_timespan()


	def chose_timespan(self):
		# get start date
		correct = False
		while not correct:
			user = raw_input(CL_TXT + 'Timespan start [' + CL_DEF + self.start + CL_TXT + ']: ' + CL_E)
			end(user)
			if not user:
				user = self.start

			# check if it's a valid date
			try:
				if len(user) == 10:
					self.start = datetime.datetime.strptime(user, '%Y/%m/%d').strftime('%Y/%m/%d')
				elif len(user) == 7:
					self.start = datetime.datetime.strptime(user, '%Y/%m').strftime('%Y/%m')
				elif len(user) == 4:
					self.start = datetime.datetime.strptime(user, '%Y').strftime('%Y')
				correct = True
			except Exception, e:
				print CL_INF + 'Please enter a valid date in the shown format.' + CL_E
				print

		# get end date
		correct = False
		while not correct:
			user = raw_input(CL_TXT + 'Timespan end [' + CL_DEF + self.ende + CL_TXT + ']: ' + CL_E)
			end(user)
			if not user:
				user = self.ende

			# check if it's a valid date
			try:
				if len(user) == 10:
					self.ende = datetime.datetime.strptime(user, '%Y/%m/%d').strftime('%Y/%m/%d')
				elif len(user) == 7:
					self.ende = datetime.datetime.strptime(user, '%Y/%m').strftime('%Y/%m')
				elif len(user) == 4:
					self.ende = datetime.datetime.strptime(user, '%Y').strftime('%Y')
				correct = True
				print
			except Exception, e:
				print CL_INF + 'Please enter a valid date in the shown format.' + CL_E
				print

		# check if mode is "count entries" or not
		# check if ouput should contain total or relative values
		if not self.count:
			correct = False
			while not correct:
				user = raw_input(CL_TXT + 'Show (t)otal or (r)elative values? [' + CL_DEF + 'total' + CL_TXT + ']: ' + CL_E)
				end(user)
				if not user:
					user = 'total'
				if user == 'r' or user == 'relative':
					self.total = '-j'
					self.span = '-p "from ' + self.start + ' to ' + self.ende + '"'
					correct = True
				elif user == 't' or user == 'total':
					# check if past values should be included, if ouput contains total values
					correct2 = False
					while not correct2:
						user = raw_input(CL_TXT + 'Include past values? [' + CL_DEF + 'yes' + CL_TXT + ']: ' + CL_E)
						end(user)
						if not user:
							user = 'yes'
						if user == 'yes' or user == 'y':
							self.span = '-d "d>=[' + self.start + '] and d<=[' + self.ende + ']"'
							correct2 = True
						elif user == 'no' or user == 'n':
							self.span = '-p "from ' + self.start + ' to ' + self.ende + '"'
							correct2 = True
						else:
							print CL_INF + 'Wrong input. Try again.' + CL_E
					correct = True
				else:
					print CL_INF + 'Wrong input. Try again.' + CL_E

		print
		self.chose_accounts()


	def chose_accounts(self):
		global ledger_file

		print CL_DIM + '(+ " not: NAME1, NAME2, ..." = exclude accounts)' + CL_E
		print CL_DIM + '(+ " par: PARAMETERS" = manual parameters)' + CL_E
		print

		correct = False
		while not correct:
			print CL_TXT + 'Accounts: ' + ', '.join(self.accnames) + CL_E
			user = raw_input(CL_TXT + 'Add account: ' + CL_E)
			end(user)
			if not user and not len(self.accounts) == 0:
				correct = True
			elif not user and len(self.accounts) == 0:
				print CL_INF + 'Please enter at least one account name.' +CL_E
			else:
				if not user in self.accnames:
					if user == ' ':
						# special function for adding all accounts at once (no exclude possible)
						if not 'All' in self.accnames:
							# add 'All' to the account names list
							self.accnames.append('All')
						else:
							print CL_INF + 'Account already added.' + CL_E
					else:
						# add user input to account names list
						if not 'not:' in user and 'par:' in user:
							# add just the name without manually added parameters
							self.accnames.append( user[0: user.find(' par:') ] )
						elif 'not:' in user and not 'par:' in user:
							# exclude accounts exists
							exc = user[user.find(' not:')+5:].split(',')
							# remove possible spaces at beginning or end of each account name and put it in ""
							exc = [x.strip(' ') for x in exc]
							# make account (with 'nots') parameter string in ""
							acc = user[0: user.find(' not:') ] + ' (not: ' + ', '.join(exc) + ')'
							self.accnames.append(acc)
						else:
							# no exclude accounts
							self.accnames.append(user)
					self.accounts.append( self.get_array(ledger_file, user) )
					# should values of this account be inverted / multiplicated by -1 ?
					user = raw_input(CL_TXT + 'Invert values of account ' + self.accnames[len(self.accnames)-1] + '? [' + CL_DEF + 'no' + CL_TXT + '] : ' + CL_E)
					if user.lower() == 'y' or user.lower() == 'yes':
						self.invert.append( True )
					else:
						self.invert.append( False )
				else:
					print CL_INF + 'Account already added.' + CL_E
			print

		print
		self.generate_plot()


	def get_range(self):
		range_min = 0
		range_max = 0

		# get max and min values
		for x in xrange(0,len(self.accounts)):
			multi = -1 if self.invert[x] else 1
			for y in xrange(0,len(self.accounts[x])):
				val = int(float(self.accounts[x][y][self.accounts[x][y].find(' ')+1:])) * multi
				if val < range_min:
					range_min = val
				if val > range_max:
					range_max = val

		# get distance between teh two values
		distance = abs(range_max - range_min)

		# return range as string for gnuplot
		if range_min >= 0:
			return '[0:' + str(range_max + (distance/7)) + ']'
		else:
			return '[' + str(range_min - (distance/7)) + ':' + str(range_max + (distance/7)) + ']'

	def generate_plot(self):
		# generate genereal settings for output plot
		debug = []
		gp = os.popen('gnuplot -persist', 'w')
		print >> gp, 'set terminal png size ' + output_size
		debug.append( 'set terminal png size ' + output_size )
		print >> gp, 'set output "' + output_file + '"'
		debug.append( 'set output "' + output_file + '"' )
		print >> gp, 'set xdata time'
		debug.append( 'set xdata time' )
		print >> gp, 'set xlabel "Date"'
		debug.append( 'set xlabel "Date"' )

		# get y range
		print >> gp, 'set yrange ' + self.get_range()
		debug.append( 'set yrange ' + self.get_range() )

		# generate settings according to self.count setting
		if self.count:
			print >> gp, 'set ylabel "N"'
			debug.append( 'set ylabel "N"' )
		elif not self.count and is_time_journal:
			print >> gp, 'set ylabel "Time"'
			debug.append( 'set ylabel "Time"' )
		else:
			print >> gp, 'set ylabel "EUR"'
			debug.append( 'set ylabel "EUR"' )
		print >> gp, 'set timefmt "' + self.rate + '"'
		debug.append( 'set timefmt "' + self.rate + '"' )

		# set up style for grid
		print >> gp, 'set grid nopolar'
		debug.append( 'set grid nopolar' )
		print >> gp, 'set grid noxtics nomxtics ytics nomytics noztics nomztics nox2tics nomx2tics noy2tics nomy2tics nocbtics nomcbtics'
		debug.append( 'set grid noxtics nomxtics ytics nomytics noztics nomztics nox2tics nomx2tics noy2tics nomy2tics nocbtics nomcbtics' )
		print >> gp, 'set grid layerdefault lt 0 linewidth 0.500, lt 0 linewidth 0.500'
		debug.append( 'set grid layerdefault lt 0 linewidth 0.500, lt 0 linewidth 0.500' )

		# set up style for graph
		if self.style == 'linespoints':
			#print >> gp, 'set style line 1 lt 1 lw 2 pt 7 ps 1.5'
			#self.style += ' ls 1'
			pass
		elif self.style == 'boxes':
			print >> gp, 'set style fill solid 0.8 border -1'
			debug.append( 'set style fill solid 0.8 border -1' )
			print >> gp, 'set boxwidth ' + str(float(1.0 / len(self.accounts)) ) + ' relative'
			debug.append( 'set boxwidth ' + str(float(1.0 / len(self.accounts)) ) + ' relative' )

		# set up box multiplicator (depends if it is for years, months or days)
		if (self.count and self.rate == '%Y-%m-%d') or (not self.count and self.frequency == ''):
			box_multi = 24
			print >> gp, 'set format x "%Y-%m-%d"'
			debug.append( 'set format x "%Y-%m-%d"' )
		elif (self.count and self.rate == '%Y-%m') or (not self.count and self.frequency == '-M'):
			box_multi = 24 * 30
			print >> gp, 'set format x "%Y-%m"'
			debug.append( 'set format x "%Y-%m"' )
			# set xtic / xlabel thing
			print >> gp, 'set xtics format "%Y-%m"'
			debug.append( 'set xticx format "%Y-%m"' )
			print >> gp, 'set xtics 60*60*24*30'
			debug.append( 'set xtics 60*60*24*30' )
		elif (self.count and self.rate == '%Y') or (not self.count and self.frequency == '-Y'):
			box_multi = 24 * 365
			print >> gp, 'set format x "%Y"'
			debug.append( 'set format x "%Y"' )
			# set xtic / xlabel thing
			print >> gp, 'set xtics format "%Y"'
			debug.append( 'set xticx format "%Y"' )
			print >> gp, 'set xtics 60*60*24*30*12'
			debug.append( 'set xtics 60*60*24*30*12' )
		else:
			box_multi = 1


		# generate plot string
		plot_str = 'plot "-" using 1:2 title "' + self.accnames[0] + '" with ' + self.style
		if self.label:
			plot_str += ', "" using 1:2:2 with labels center offset 0,1 notitle'
		for x in xrange(1,len(self.accounts)):
			if self.style == 'boxes':
				tmp_using = '(timecolumn(1)+3600*' + str( float(1.0 / len(self.accounts)) * x * box_multi ) + '):2'
			else:
				tmp_using = '1:2'
			plot_str += ', "" using ' + tmp_using + ' title "' + self.accnames[x] + '" with ' + self.style
			if self.label:
				plot_str += ', "" using ' + tmp_using + ':2 with labels center offset 0,1 notitle'
		print >> gp, plot_str
		debug.append( plot_str )


		# generate data for all the selected accounts
		for x in xrange(0,len(self.accounts)):
			multi = -1 if self.invert[x] else 1
			for y in xrange(0,len(self.accounts[x])):
				print >> gp, str( self.accounts[x][y][0:self.accounts[x][y].find(' ')] + ' ' + str(int(float(self.accounts[x][y][self.accounts[x][y].find(' ')+1:])) * multi) )
				debug.append( str( self.accounts[x][y][0:self.accounts[x][y].find(' ')] + ' ' + str(int(float(self.accounts[x][y][self.accounts[x][y].find(' ')+1:])) * multi ) ) )
			print >> gp, 'e'
			debug.append( 'e' )

			if self.label:
				for y in xrange(0,len(self.accounts[x])):
					multi = -1 if self.invert[x] else 1
					# round the output number
					print >> gp, str( self.accounts[x][y][0:self.accounts[x][y].find(' ')] + ' ' + str(int(round(float(self.accounts[x][y][self.accounts[x][y].find(' ')+1:]))) * multi) )
					debug.append( str( self.accounts[x][y][0:self.accounts[x][y].find(' ')] + ' ' + str(int(round(float(self.accounts[x][y][self.accounts[x][y].find(' ')+1:]))) * multi) ) )
				print >> gp, 'e'
				debug.append( 'e' )

		# debug ouput
		if debug_output:
			print
			print 'Debug output:'
			print '--- --- ---'
			for x in debug:
				print x
			print '--- --- ---'
			print



# start
plot = plot_class()
plot.chose_style()