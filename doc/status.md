# Status

## Job

`JobStatus.CREATED`
`JobStatus.PENDING`
`JobStatus.RUNNING`
`JobStatus.FAILED`
`JobStatus.SUCCESS`
`JobStatus.CANCELED`
`JobStatus.SKIPPED`
`JobStatus.ERROR`

## Stage

`StageStatus.CREATED`
`StageStatus.PENDING`
`StageStatus.RUNNING`
`StageStatus.FAILED`
`StageStatus.SUCCESS`
`StageStatus.CANCELED`
`StageStatus.SKIPPED`
`StageStatus.ERROR`

`JobStatus.RUNNING in statuses` → `StageStatus.RUNNING`
`JobStatus.PENDING in statuses` → `StageStatus.PENDING`
`JobStatus.CREATED in statuses` → `StageStatus.CREATED`
`JobStatus.ERROR in statuses` → `StageStatus.ERROR`
`JobStatus.FAILED in statuses` → `StageStatus.FAILED`
`JobStatus.CANCELED in statuses` → `StageStatus.CANCELED`
`JobStatus.SKIPPED in statuses` → `StageStatus.SKIPPED`