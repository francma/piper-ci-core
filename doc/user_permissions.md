# User permissions

## Global

* `UserRole.ROOT`
* `UserRole.ADMIN`
* `UserRole.NORMAL`
* `UserRole.GUEST`

## Project

* `ProjectRole.MASTER`
* `ProjectRole.DEVELOPER`

`UserRole.USER` can not be `ProjectRole.MASTER`

# Models

## User (1)

|        | `UserRole.ROOT` | `UserRole.ADMIN` | `UserRole.NORMAL` | `UserRole.GUEST` |
|:-------|:----------------|:-----------------|:----------------|:----------------|
| View   | ✓               | ✓                |                 | |
| Create | ✓               | ✓ (2)            |                 | |
| Edit   | ✓               |                  |                 | |
| Delete | ✓               |                  |                 | |

(1) User can edit/delete/view self

(2) UserRole.Admin can add only Users with UserRole.USER

## Runner

|        | `UserRole.ROOT` | `UserRole.ADMIN` | `UserRole.NORMAL` | `UserRole.GUEST` |
|:-------|:----------------|:-----------------|:----------------|:----------------|
| View   | ✓               | ✓                | ✓               | |
| Create | ✓               |                  |                 | |
| Edit   | ✓               |                  |                 | |
| Delete | ✓               |                  |                 | |

## Project

|        | `UserRole.ROOT` | `UserRole.ADMIN` | `UserRole.NORMAL` | `UserRole.GUEST` |
|:-------|:----------------|:-----------------|:----------------|:----------------|
| View | ✓               | ✓                |  ✓               | ✓ |
| Create | ✓               | ✓                |                 | |

|        | `UserRole.ROOT` | `ProjectRole.MASTER` | `ProjectRole.DEVELOPER` | `ProjectRole.GUEST` |
|:-------|:----------------|:---------------------|:------------------------|:--------------------|
| Edit   | ✓               | ✓                    |                         |                     |
| Delete | ✓               | ✓                    |                         |                     |

## Project Users

|        | `UserRole.ROOT` | `ProjectRole.MASTER` | `ProjectRole.DEVELOPER` |
|:-------|:----------------|:---------------------|:------------------------|
| View   | ✓               | ✓                    |                         |
| Create | ✓               | ✓                    |                         |
| Delete | ✓               | ✓                    | ✓ (1)                   |

(1) Only self

## Build/Stage/Job (1)

|        | `UserRole.ROOT` | `ProjectRole.MASTER` | `ProjectRole.DEVELOPER` | `UserRole.GUEST` |
|:-------|:----------------|:---------------------|:------------------------|:--------------------|
| Cancel | ✓               | ✓                    | ✓                       |                     |
| Restart | ✓               | ✓                    | ✓                       |                     |

(1) Everyone can view builds