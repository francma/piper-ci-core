# Úvod

Veškerá komunikace s řídící komponentou bude probíhat přes REST API.

## Uživatelé

- /users [GET, POST]
- /users/\<userId\> [PATCH, DELETE]

## Projekty

- /projects [GET, POST]
- /projects/\<projectId\> [GET, PATCH, DELETE]

## Kontejnery

- /containers [GET, POST]
- /containers/\<containerId\> [GET, PATCH, DELETE]

## Build

- /build [GET, POST]
- /build/pop/\<containerSecret\> [GET]
- /build/\<buildId\>/ [GET]

## Streaming log

- /build/stream [WS]