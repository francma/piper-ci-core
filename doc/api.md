# API

## `/runner`

### GET

## `/runner/<id>`

### GET

### POST

Edituj runner

### PUT

## `/runner/<id>/project`

### GET

Vrat mi list s ID projekty ktere ma runner prirazeno

### POST

Pridej projekt k runneru.

## `/runner/<id>/project/<id>`

### DEL

Odeber projekt s <id> od runneru.

## `/project`

### GET

### POST

## `/project/<id>`

### GET

### PUT

### DELETE

## `/project/<id>/user`

### POST

### GET

## `/project/<id>/user/<id>`

### DEL

### PUT

### GET

## `/project/<id>/runner`

### POST

### GET

## `/project/<id>/runner/<id>`

### DEL

## `/build`

### GET

(filters: project_id, user_id)

## `/build/<id>`

### GET

### DELETE

### PUT

## `/stage`  (filters: build_id, project_id, user_id)

### GET

## `/stage/<id>`

### GET

### PUT

### DEL

## `/job` (filters: build_id, project_id, stage_id, user_id)

### GET

## `/job/<id>`

### GET

### DEL

### PUT