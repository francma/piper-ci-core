import yaml

from piper_driver.models import *


def test_basic(connection):
    with open('tests/configs/basic.yml') as fd:
        contents = yaml.load(fd)

    project = Project()
    project.origin = 'TEST'
    project.url = 'TEST'
    project.save()

    build = Build()
    build.project = project
    build.branch = 'TEST'
    build.commit = '634721d9da222050d41dce164d9de35fe475aa7a'
    build.load_config(contents)
