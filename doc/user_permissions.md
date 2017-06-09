# User permissions

## Global

* `UserRole.ROOT`
* `UserRole.ADMIN`
* `UserRole.USER`

## Project

* `ProjectRole.MASTER`
* `ProjectRole.DEVELOPER`
* `ProjectRole.GUEST`

`UserRole.USER` can not be `ProjectRole.MASTER`

# Models

## User (1)

|        | `UserRole.ROOT` | `UserRole.ADMIN` | `UserRole.USER` |
|:-------|:----------------|:-----------------|:----------------|
| View   | ✓               | ✓                |                 |
| Create | ✓               | ✓ (2)            |                 |
| Edit   | ✓               |                  |                 |
| Delete | ✓               |                  |                 |

(1) User can edit/delete self
(2) UserRole.Admin can add only Users with UserRole.USER

## Runner

|        | `UserRole.ROOT` | `UserRole.ADMIN` | `UserRole.USER` |
|:-------|:----------------|:-----------------|:----------------|
| View   | ✓               | ✓                | ✓               |
| Create | ✓               |                  |                 |
| Edit   | ✓               |                  |                 |
| Delete | ✓               |                  |                 |

## Project

|        | `UserRole.ROOT` | `UserRole.ADMIN` | `UserRole.USER` |
|:-------|:----------------|:-----------------|:----------------|
| Create | ✓               | ✓                |                 |

|        | `UserRole.ROOT` | `ProjectRole.MASTER` | `ProjectRole.DEVELOPER` | `ProjectRole.GUEST` |
|:-------|:----------------|:---------------------|:------------------------|:--------------------|
| View   | ✓               | ✓                    | ✓                       | ✓                   |
| Edit   | ✓               | ✓                    |                         |                     |
| Delete | ✓               | ✓                    |                         |                     |

## Project Users

|        | `UserRole.ROOT` | `ProjectRole.MASTER` | `ProjectRole.DEVELOPER` | `ProjectRole.GUEST` |
|:-------|:----------------|:---------------------|:------------------------|:--------------------|
| View   | ✓               | ✓                    |                         |                     |
| Create | ✓               | ✓                    |                         |                     |
| Delete | ✓               | ✓                    | ✓ (1)                   | ✓ (1)               |

(1) Only self

## Project Runner

|        | `UserRole.ROOT` | `ProjectRole.MASTER` | `ProjectRole.DEVELOPER` | `ProjectRole.GUEST` |
|:-------|:----------------|:---------------------|:------------------------|:--------------------|
| Create | ✓               | ✓                    |                         |                     |
| Delete | ✓               | ✓                    |                         |                     |

## Build/Stage/Job

|        | `UserRole.ROOT` | `ProjectRole.MASTER` | `ProjectRole.DEVELOPER` | `ProjectRole.GUEST` |
|:-------|:----------------|:---------------------|:------------------------|:--------------------|
| View   | ✓               | ✓                    | ✓                       | ✓                   |
| Cancel | ✓               | ✓                    | ✓                       |                     |
