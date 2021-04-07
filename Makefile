help:
	@echo  'Commands:'
	@echo  '  autoformat   - Run black on all the source files, to format them automatically'
	@echo  '  verify       - Run a bunch of checks, to see if there are any obvious deficiencies in the code'
	@echo  ''

autoformat:
	black -l 120 app.py gtfs_realtime.py structures.py util.py constants.py

verify:
	black -l 120 --check app.py gtfs_realtime.py structures.py util.py constants.py
	flake8 --config=.flake8 app.py gtfs_realtime.py structures.py util.py constants.py
	bandit app.py gtfs_realtime.py structures.py util.py constants.py
