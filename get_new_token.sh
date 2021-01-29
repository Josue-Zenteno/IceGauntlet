#!/usr/bin/expect -f

set number_arguments [llength $argv]

if {"$number_arguments" > 2 } {
    set user [lindex $argv 0]
    set password [lindex $argv 1]
    set proxy [lindex $argv 2]

    spawn -noecho python3 ./src/auth_client.py "$user" "$proxy" -t
    expect "Password:"
    send "$password\r"
    interact
} else {
    spawn echo "Command arguments: <user> <password> <proxy>"
}