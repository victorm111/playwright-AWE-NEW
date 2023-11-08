# README.md
# Project Title

Python running Playwright automation tests (chromium), login, retain separate contexts to check:
1. search and replay :: calls found in 24hr window? fails if no calls found
2. Capture Verification:: call recording issues found in 24hur window? fails if calls found

## Getting Started

PyCharm script path and working dir:
..\PycharmProjects\playwright-AWE

### Prerequisites

see requirements.txt for package reqt
```
Give examples
```

### Installing

add https interface for pip package updates, add pip.ini file with:

# for system-wide configuration file
[global]
trusted-host = pypi.python.org
               pypi.org
               raw.githubusercontent.com
               files.pythonhosted.org


install steps:
install PyCharm

$ pip3 install playwright
$ pip3 install pytest
$ pip3 install pytest-playwright

$ pip3 install -r requirements.txt
$ playwright install

install Playwright >>install browsers

import project
pip install -r requirements.txt

## project layout
config: includes input config filr
logs: incl pytest logs
output: additional logs and output files
pages: page object model files, model webpages
report: html report 
tests: test code

.env: env file
conftest.py : global routines
pytest.ini: pytest init file
requirements.txt: required packages


## Running the tests
# PyCharm option:
-n 1 --count=1 (-n runs on number CPUs, --count number of tests to run one after another
pytest.ini -n 3 runs on 3 procs, can run tests in parallel

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

Victor Whitmarsh

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License



## Acknowledgments


