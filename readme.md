# Ledger plot

## Short description

An approach to an easy to use interface for plotting ledger journals with GNUplot.


## Usage

Start the code with a valid ledger journal as a parameter. For example:

	python ledger-plot.py /home/user/ledger_files/ledger_2015.journal

Then you can chose a style for the plotting:

	(1) Lines
	(2) Linespoints
	(3) Boxes
	(4) Linespoints (Autozero)
	(5) Boxes (Autozero)
	Style [1]: 2

Let's chose 2. Afterwards we can chose the mode. Chosing `no` will make a plot according to the values of the transactions in the ledger journal. Chosing `yes` would make a plot according to the *number* of transactions of the specific account. Pressing `enter` will chose the defautl value: no.

	Count entries? [no]:

	Timespan start [1900/01/01]:

Now we have to set up the time span: start and end date. Just pressing `enter` two times, will probably chose all the journal entries (except you have entries before the 19th century or after the 99th).

After this we have to chose, if we want the plot to show us the total amount of the account value, or just the relative values (the amount which was added or subtracted from the specific account). Let's chose total / default.

	Show (t)otal or (r)elative values? [total]:
	Include past values? [yes]:

Now we can chose if the values before the time span should be included in the calculation or not. It won't make a difference, if there is no start date set, since it would add the values anyway. Let's chose yes / default, which will bring us to the final entry option:

	Accounts:
	Add account:

Here we see the added accounts and the entry field in which we can add an account. Maybe we have three accounts, but want just two to be plotted. Let's enter them, one for every entry field. The accounts could be `Car Stuff` and `Health` for example. The final output should show this:

	Accounts:
	Add account: Car Stuff

	Accounts: Car Stuff
	Add account: Health

	Accounts: Car Stuff, Health
	Add account:

When pressing `enter` now, the plotting will begin and output a file (specified in the python code in the configuration area).

You can quit the program, by entering `.` in any entry field.