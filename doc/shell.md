# Shell

* `user`
  * `user get [user_id]`
  * `user list [filter=value] ...`
  * `user create [property=value] ...`
  * `user update [user_id] [property=value] ...`
  * `user delete [user_id]`
* `identity`
  * `identity get`
  * `identity update [property=value] ...`
* `runner`
  * `runner get [runner_id]`
  * `runner list [runner_id] [filter=value] ...`
  * `runner create [property=value] ...`
  * `runner update [runner_id] [id] [property=value] ...`
  * `runner delete [runner_id]`
* `project`
  * `project get [project_id]`
  * `project list [filter=value] ...`
  * `project create [property=value] ...`
  * `project update [project_id] [property=value] ...`
  * `project delete [project_id]`
  * `project user-list [project_id]`
  * `project user-add [project_id] [user_id]`
  * `project user-remove [project_id] [user_id]`
* `build`
  * `build get [build_id]`
  * `build list [build_id] [filter=value] ...`
  * `build cancel [build_id]`
  * `build restart [build_id]`
* `stage`
  * `stage get [stage_id]`
  * `stage list [stage_id] [filter=value] ...`
  * `stage cancel [stage_id]`
  * `stage restart [stage_id]`
* `job`
  * `job get [job_id]`
  * `job list [job_id] [filter=value] ...`
  * `job cancel [job_id]`
  * `job restart [job_id]`
  * `job log [job_id]`


