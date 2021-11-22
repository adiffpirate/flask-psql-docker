#!/bin/bash

if [ -f /.init_control/run_timestamp ]; then

	echo >&2 "The database was already initialized before. Skipping script execution."

else

	while ! nc -z db 5432; do
		echo >&2 "Waiting for database"
		sleep 1
	done

	python3 /init.py

	date '+%Y%m%d-%H%M%S' > /.init_control/run_timestamp
	echo >&2 "Saving timestamp at /.init_control/run_timestamp. DO NOT DELETE THIS FILE!"

fi
