# Runner job status report

Request (runner → driver):

url = `/job/report?status=[STATUS]`

STATUS in {ERROR, RUNNING, COMPLETED}

Response (driver → runner)

{
    status: {OK, CANCEL, ERROR}
}