# User permissions

## Global

* UserRole.MASTER
* UserRole.ADMIN
* UserRole.NORMAL

## Project

* ProjectRole.MASTER
* ProjectRole.DEVELOPER
* ProjectRole.GUEST

UserRole.NORMAL can not be ProjectRole.MASTER

## User

|        | UserRole.MASTER | UserRole.ADMIN | UserRole.NORMAL |
|--------|-----------------|----------------|-----------------|
| Create | Yes             | Yes (*)        | No              |
| Edit   | Yes             | No             | No              |
| View   | Yes             | No             | No              |

(*) UserRole.Admin can add only Users with UserRole.NORMAL

## Runner

|        | UserRole.MASTER | UserRole.ADMIN | UserRole.NORMAL |
|--------|-----------------|----------------|-----------------|
| View   | Yes             | Yes            | No              |
| Create | Yes             | No             | No              |
| Edit   | Yes             | No             | No              |
| Delete | Yes             | No             | No              |

## Project

|        | UserRole.MASTER | UserRole.ADMIN | UserRole.NORMAL |
|--------|-----------------|----------------|-----------------|
| Create | Yes             | Yes            | No              |

|        | UserRole.MASTER | ProjectRole.MASTER | ProjectRole.DEVELOPER | ProjectRole.GUEST |
|--------|-----------------|--------------------|-----------------------|-------------------|
| View   | Yes             | Yes                | Yes                   | Yes               |
| Edit   | Yes             | Yes                | No                    | No                |
| Delete | Yes             | Yes                | No                    | No                |

## Project Users

|        | UserRole.MASTER | ProjectRole.MASTER | ProjectRole.DEVELOPER | ProjectRole.GUEST |
|--------|-----------------|--------------------|-----------------------|-------------------|
| View   | Yes             | Yes                | No                    | No                |
| Create | Yes             | Yes                | No                    | No                |
| Delete | Yes             | Yes                | No                    | No                |

## Project Runner

|        | UserRole.MASTER | ProjectRole.MASTER | ProjectRole.DEVELOPER | ProjectRole.GUEST |
|--------|-----------------|--------------------|-----------------------|-------------------|
| Create | Yes             | Yes                | No                    | No                |
| Delete | Yes             | Yes                | No                    | No                |

## Build/Stage/Job

|        | UserRole.MASTER | ProjectRole.MASTER | ProjectRole.DEVELOPER | ProjectRole.GUEST |
|--------|-----------------|--------------------|-----------------------|-------------------|
| View   | Yes             | Yes                | Yes                   | Yes               |
| Cancel | Yes             | Yes                | Yes                   | No                |
