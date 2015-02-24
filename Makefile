all:
	pyinstaller --distpath=bin --workpath=pyinstaller -n microanalytics --onefile --log-level DEBUG microanalytics.py
	rm -r pyinstaller
