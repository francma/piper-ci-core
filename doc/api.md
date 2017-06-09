# API structure

*  `/runners`
   *  `/runners/[id]`
* `/projects`
  * `/projects/[project_id]`
  * `/projects/[project_id]/builds` → `/build?project=[project_id]`
  * `/projects/[project_id]/stages` → `/stages?project=[project_id]`
  * `/projects/[project_id]/jobs` → `/jobs?project=[project_id]`
  * `/projects/[project_id]/users`
  * `/projects/[project_id]/users/[user_id]`
* `/builds`
  * `/builds/[build_id]`
  * `/builds/[build_id]/cancel`
  * `/builds/[build_id]/restart`
  * `/builds/[build_id]/stages` → `/stages?build=[build_id]`
  * `/builds/[build_id]/jobs` → `/jobs?build=[build_id]`
* `/stages`
  * `/stages/[stage_id]`
  * `/stages/[stage_id]/cancel`
  * `/stages/[stage_id]/restart`
  * `/stages/[stage_id]/jobs` → `/jobs?stage=[stage_id]`
* `/jobs`
  * `/jobs/[job_id]`
  * `/jobs/[job_id]/cancel`
  * `/jobs/[job_id]/restart`
  * `/jobs/[job_id]/log`
  * `/jobs/queue/[runner_token]`
  * `/jobs/report/[job_secret]`
* `/identity`
* `/users`
  * `/users/[user_id]`
* `/webhook`


## `/projects`

## `/builds`

Filters
* project = int

## `/stages`

Filters
* build = int
* project = int

## `/jobs`

Filters:
* project = int
* build = int
* stage = int
