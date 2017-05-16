from piper_driver.models import *


def test_basic(connection):
    with open('tests/configs/basic.yml') as fd:
        contents = fd.read()

    project = Project()
    project.origin = 'TEST'
    project.url = 'TEST'
    project.save()

    group = RunnerGroup()
    group.name = 'RUNNER'
    group.save()

    build = Build()
    build.project = project
    build.ref = 'TEST'
    build.commit = '634721d9da222050d41dce164d9de35fe475aa7a'
    load_config(build, contents)

