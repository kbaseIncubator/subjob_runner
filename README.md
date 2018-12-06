# KBase Module Subjob Runner

> Work in progress

Call other KBase module methods from within a running app.

While a KBase App is running, it can call methods on other apps by starting up separate docker containers, running commands, tracking job results, and keeping a log of everything (which can be used to generate data provenance).

## Installing

_Requirements_
* Python 3.5+ and pip 9+

See [`.env.example`](/.env.example) for environment variables to set.

## Running

```sh
$ make serve
```

## Development

### Testing

With the server running on localhost:5000, run:

```sh
$ make test
```

### How it works
