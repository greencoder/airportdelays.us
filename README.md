# airportdelays.us
Python code to generate airportdelays.us site

## Usage

The program is broken into two parts. The first will create a JSON data file with airport delays. The second will generate an HTML page from the delays data file.

**Generating the delay.json file**

The `scrape.py` program will call the FAA website and identify the airports with delays. It will create the `delay.json` file:

```
$ python scrape.py
```

**Generating the HTML page**

The `generate.py` program will use the `delay.json` file and the `index.tpl.html` Jinja2 template to generate the `index.html` page:

```
$ python generate.py
```
