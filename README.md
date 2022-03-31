# AlgoSeek First Assignment

First assignment provided by AlgoSeek in order to identify stocks with
erroneous identifiers. The idea is the following:

1. A stock has a mapping from a Ticker Space to an Identifier Space
2. This mapping changes periodically. For instance, a  specific ticker may be mapped to different IDs on different periods.

## The Problem

On some days some tickers may appear multiple times with different IDs.
However, on each day only one ID should be available. We should remove  such entries.
If a Ticker appears multiple times with the correct ID it can be assumed as a non problem in my understanding. 
However, I don't understand in such a case what the second record actually represents.

## How to Run?

This is a dockerized project. As a result you need to use the following commands in order
to build the docker container.

1. Build the Docker Imager
```bash
docker build -t algoseek .
```
2. Run the algoseek container
```bash
docker run -t -d --name algoseek_container algoseek
```
Note: If you want to mount the results folder:
```bash
docker run -t -d -v results:/app/results/ --name algoseek_container algoseek
```
3. Attach to the Docker container
```bash
docker exec -it algoseek_container /bin/bash
```

### Inside Docker

1. Run python cli.py in order to view the available commands.

```bash
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

      _   _          ___          _     ___ _        _     _____        _
     /_\ | |__ _ ___/ __| ___ ___| |__ | __(_)_ _ __| |_  |_   _|_ _ __| |__
    / _ \| / _` / _ \__ \/ -_) -_) / / | _|| | '_(_-<  _|   | |/ _` (_-< / /
   /_/ \_\_\__, \___/___/\___\___|_\_\ |_| |_|_| /__/\__|   |_|\__,_/__/_\_\ 
           |___/

Options:
  --help  Show this message and exit.

Commands:
  fix-errors       Fix the errors of the input files.
  identify-errors  Identify the errors of the input files.

```

2. Run the error identifier
```bash
python cli.py error-identifier
```

The results will be provided in `./results/problematic_indices.json`.

3. Run error fixer
```bash
python cli.py fix-errors
```
The results will be provided in `./results/` using the original format.

### Help I Need Fast Run

Use:
```bash
python cli.py error-identifier --year 2007
```
```bash
python cli.py fix-errors --year 2007
```

### New! Parallel Processes

In order to run the scripts using multiple cores we need  to utilized multiple processes.
This is due to the weakness of Python because of Global Interpreter Lock (GIL).

**Warning:** Since processes are not light and do not share the process addresses 
the more the processes the more the RAM required.

**Why?** Each process will need a copy of the data structures.

**Use:**
```bash
python cli.py error-identifier --year 2007 --workers 4
```

```commandline
Usage: cli.py identify-errors [OPTIONS]

  Identify the errors of the input files. The output is provided at
  results/identified with the same format.

  Arguments:
      export (bool): Export the lines with errors.
      year (str): The year to check for errors. If not specified all years are used. Default is None.
      workers (int): How many workers to use. Default 1.

Options:
  -y, --year TEXT              The year to fix. Use None for all the years.
  -e, --export BOOLEAN         Export the identified lines as a JSON file.
  -w, --workers INTEGER RANGE  The number of workers.  [1<=x<=10]
  --help                       Show this message and exit.

```

```bash
python cli.py fix-errors --year 2007 --workers 4
```
```commandline
Usage: cli.py fix-errors [OPTIONS]

  Fix the errors of the input files. The output is provided at results/fixed/
  with the same format.

  Arguments:
      year (str): The year to check for errors. If not specified all years are used. Default is None.
      workers (int): How many workers to use. Default 1.

Options:
  -y, --year TEXT              The year to fix. Use None for all the years.
  -w, --workers INTEGER RANGE  The number of workers.  [1<=x<=10]
  --help                       Show this message and exit.

```

**Warning:** If you use a simple worker the old implementation is utilized.