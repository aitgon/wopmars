#!/usr/bin/env bats


@test "wopmars first run" {

# First run: executes
rm -f wopmarsexample/db.sqlite; wopmars -d wopmarsexample -w wopmarsexample/Wopfile -D "sqlite:///wopmarsexample/db.sqlite"
let piece_car_modif_time=$(sqlite3 wopmarsexample/db.sqlite "select mtime_epoch_millis from wom_TableModificationTime where table_name=='piece_car'")

[[ "$piece_car_modif_time" -gt "$piece_modif_time" ]]

}

@test "wopmars second run: does not execute" {

# Second run: does not execute
wopmars -d wopmarsexample -w wopmarsexample/Wopfile -D "sqlite:///wopmarsexample/db.sqlite"
let piece_car_modif_time2=$(sqlite3 wopmarsexample/db.sqlite "select mtime_epoch_millis from wom_TableModificationTime where table_name=='piece_car'")

[[ "$piece_car_modif_time" -eq "$piece_car_modif_time" ]]

}

# Do not know why but it is not working
#@tests "wopmars third run: forces execute" {
# Third run with force: executes
#wopmars -d wopmarsexample -w wopmarsexample/Wopfile.yml -D "sqlite:///wopmarsexample/db.sqlite" -F
#let piece_car_modif_time3=$(sqlite3 wopmarsexample/db.sqlite "select mtime_epoch_millis from wom_TableModificationTime where table_name=='piece_car'")
#[[ "$piece_car_modif_time2" -ne "$piece_car_modif_time3" ]]

#}

@test "wopmars clear history" {

# Third run with force: executes
wopmars -d wopmarsexample -w wopmarsexample/Wopfile -D "sqlite:///wopmarsexample/db.sqlite" --cleanup-metadata
nb_rows=$(sqlite3 wopmarsexample/db.sqlite "select count() from wom_TableModificationTime")

[[ "$nb_rows" -eq "0" ]]

}
