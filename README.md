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

To view an example survey (without having to have a running version of `eq-author`), simply append the parameter: `debug=True`
example:

  `http://127.0.0.1:5000/questionnaire/1/ABCD?debug=True`

Where `ABCD` is the questionnaire session ID and `1` is the questionnaire ID.


# How to run using docker locally


## Pre-requistes

__Mac__

1. Install docker-toolkit: https://www.docker.com/toolbox
2. Install Virtualbox > 4.3.28 : https://www.virtualbox.org/wiki/Downloads
3. Once installed, run the following:
```
docker-machine create default
eval "$(docker-machine env default)"
```
This will create a virtual machine as your docker host and populate your
environment with the correct values to use docker as a linux system would.
Everytime you start or stop a docker-machine VM instance, you need to
re-run `eval "$(docker-machine env default)"`.

__AWS__
The survey runner deposits submitted responses in an S3 bucket. To be able to do this it needs to know your aws details.
PIP will install the aws cli for you, however you need to run `aws configure` in order to place the necessary files in
your home directory.

__Ubuntu__

1. Run 'curl -sSL https://get.docker.com/ | sh'
2. Follow the instructions here to create a docker group: https://docs.docker.com/installation/ubuntulinux/
3. Install `docker-compose` using pip globally: `sudo pip install  -U docker-compose`


## Bring up a local docker dev environment

1. Clone this repo locally: `git clone https://github.com/onsdigital/eq-survey-runner.git`
2. CD into the new folder `eq-survey-runner`
3. Run `docker-compose up`
4. Go make tea / coffee / alternative while you pull down all the necessary docker images.
5. You should now have two docker instances, running the survey-runner application and cassandra, linked
and supporting partial saving of form data.
6. In a terminal run `docker-machine ip default` and then visit that IP address on port 8080 to view
the survey runner app.

__NOTE__: Any changes you make on your *local* machine to eq-survey-runner files should automatically trigger
a reload of the webserver. To inspect inside the container, grab the docker instances CONTAINER ID and run
`sudo docker exec -i -t <CONTAINER_ID> bash`


## Common fixes to known issues with docker-machine

1. "Network timed out while trying to connect to https://index.docker.io/v1/repositories/spotify/cassandra/images. You may want to check your internet connection or if you are behind a proxy."
__Fix__:

Run the following in the commandline:

```
 docker-machine restart default      # Restart the environment
 eval $(docker-machine env default)  # Refresh your environment settings
```
Sometimes it seems docker-machine gets in a weird state. ¯\_(ツ)_/¯


## How to run the test suite

`python srunner_tests.py`
