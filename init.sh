#!/bin/bash
# Folder required for the bot to actually save lua code
mkdir -p luacode

# Here for future-proofing, in case the name changes for some reason
DB="data.db"

# This code is used when a failure should be returned,
# but we still want the rest of the code to run
EXITCODE=0

# Makes luap
if [ ! -e luap ] && [ ! -e luac ]; then
	cd ./luapc
	echo "Compiling luap"
	make && echo "Compiled luap" || echo "luap failed to compile"
	cd ..
fi

# Generates the data.db
if [ ! -e "$DB" ] ;then
	echo "Creating $DB"
	if command -v sqlite3 > /dev/null 2>&1; then
		sqlite3 "$DB" <<- ENDSQL
			CREATE TABLE IF NOT EXISTS "quotes" (
				"id"	INTEGER,
				"quote"	TEXT,
				PRIMARY KEY("id")
			);
			CREATE TABLE IF NOT EXISTS "servers" (
				"server"	INTEGER,
				"join_chat"	INTEGER
			);
			CREATE TABLE IF NOT EXISTS "sorts" (
				"type"	INTEGER,
				"message"	INTEGER,
				"channel"	INTEGER,
				"amount"	INTEGER,
				"list"	TEXT
			);
		ENDSQL
	else
		echo "Cannot find the sqlite3 CLI, cannot create $DB"
		[ $EXITCODE ] || EXITCODE=1
	fi
fi

exit $EXITCODE
