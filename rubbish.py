@app.route('/project/<project_id>/add-build', methods=['POST'])
def add_build(project_id):
    """
    {
        stages: {first, second, third},
        jobs: {
            job1: {
                stage: first
                config: {}
                commands: [a, b, c]
            }
        }
    }

    :return: 
    """
    json_input = flask.request.get_json()
    stages = {}
    jobs = []
    commands = []

    project = Project.get(Project.id == project_id)

    build = Build(status=BuildStatus.NEW, project=project)

    first_stage = None
    for idx, stage_name in enumerate(json_input['stages']):
        stage = Stage(name=stage_name, order=idx, status=StageStatus.NEW, build=build)
        stages[stage_name] = stage
        if idx == 0:
            first_stage = stage

    for idx, job_name in enumerate(json_input['jobs']):
        job_def = json_input['jobs'][job_name]
        job = Job(stage=stages[job_def['stage']], status=JobStatus.NEW)
        jobs.append(job)
        for command_idx, command_def in enumerate(job_def['commands']):
            command = Command(job=job, command=command_def, type=CommandType.SCRIPT)
            commands.append(command)

    build.save()

    for key, stage in stages.items():
        stage.save()

    for job in jobs:
        job.save()

    for command in commands:
        command.save()

    query = Job.select().where(Job.stage == first_stage)
    for job in query:
        project.push_job(job)

    response = flask.make_response('', 201)

    return response


@app.route('/build/pop/<token>', methods=['GET'])
def pop_build(token):
    # get piper_lxd
    try:
        runner = Runner.get(Runner.token == token)
    # FIXME catch 'smaller' exception
    except Exception:
        flask.abort(404)

    # get projects associated with piper_lxd
    projects = runner.projects()
    projects = [x for x in projects]

    # randomly select project queue and get job
    order = list(range(len(projects)))
    random.shuffle(order)
    for i in order:
        job = projects[i].pop_job()
        if job is not None:
            break

    # return empty response if we don't have any job
    if job is None:
        return ''

    # mark job as sent
    @app.after_this_request
    def mark_job_as_sent(response):
        job.status = JobStatus.SENT
        job.save()

    # export job as json
    export = job.runner_export()

    return flask.jsonify(export)


@ws.route('/write-build')
def write_build(socket):
    # get secret query parameter
    with app.request_context(socket.environ):
        args = flask.request.args
        secret = args['secret'] if args['secret'] else None

    # get build
    try:
        job = Job.get(Job.secret == secret)
    # FIXME catch 'smaller' exception
    except Exception:
        socket.close('Invalid secret')

    handler = SocketHandler(socket)
    file_listener = FileListener(os.path.join(BUILD_LOG_FOLDER, str(job.id)))
    handler.add_listener(file_listener)
    handler.receive()


@ws.route('/read-build-log')
def read_build_log(socket):
    with app.request_context(socket.environ):
        args = flask.request.args
        secret = args['secret']

    idx = 0
    fd = None

    # TMP hack: wait for first file
    while True:
        try:
            path = os.path.join('build', '{}.{}'.format(secret, idx))
            fd = os.open(path, os.O_RDONLY)
            break
        except OSError as e:
            print(e)
            time.sleep(.1)
            continue

    socket.send('{} {}\n'.format('$', script[idx]))

    while True:
        time.sleep(.1)
        output = os.read(fd, 1000)
        if output == b'':
            path = os.path.join('build', '{}.{}'.format(secret, idx + 1))
            if os.path.isfile(path):
                idx += 1
                os.close(fd)
                fd = os.open(path, os.O_RDONLY)
                socket.send('{} {}\n'.format('$', script[idx]))
            continue
        socket.send(output.decode('utf-8'))

class SocketHandler:

    def __init__(self, socket):
        self.socket = socket
        self.listeners = []

    def receive(self):
        while True:
            data = self.socket.receive()
            if data is not None:
                for listener in self.listeners:
                    listener.on_message(data)
            else:
                return

    def add_listener(self, listener):
        self.listeners.append(listener)


class FileListener:

    def __init__(self, path):
        self.fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)

    def on_message(self, data):
        os.write(self.fd, data)
        os.fsync(self.fd)