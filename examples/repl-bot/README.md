# repl-bot

This project demonstrates something a bit more complex than the `simple-demo`, as well as a better project structure

A slash command named `/exec` is defined that takes a string argument. This string is run through `exec`, and any output is returned in a message.

## Running

```bash
$ git clone https://github.com/buckley-w-david/flask-discord-interactions.git
$ cd flask-discord-interactions/examples/repl-bot
$ export DISCORD_PUBLIC_KEY="..."
$ export DISCORD_CLIENT_ID="..."
$ export DISCORD_CLIENT_SECRET="..."
$ poetry install
$ FLASK_APP=repl_bot poetry run flask run
```
