# eq-survey-runner
EQ Survey runner for executing and collecting survey responses.


## Pre-install
This assumes an Ubuntu development environment, but should be portable to any linux/BSD
related system.

1. Ensure you have python3.4 or greater installed.
2. Download pip and virtualenv (virtualenvwrapper may also be helpful)
3. (Optional) for running in a Heroku like environment locally you may find
it helpful to install Heroku local toolbelt.
`wget -O- https://toolbelt.heroku.com/install-ubuntu.sh | sh`


## How to install and start development

1. Create a new virtualenv
2. Activate the virtualenv
3. Clone this repo local. `git clone git@github.com:ONSdigital/eq-survey-runner.git`
4. Install the dependencies using pip: `pip install -r requirements.txt`
5. Run the test suite to check everything is working well: `python srunner_tests.py`
6. Optional: to run the application locally using Heroku toolbelt, run `heroku local`


## How to run the test suite

`python srunner_tests.py`
