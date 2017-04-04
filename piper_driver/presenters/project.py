from flask_restful import Resource, abort
from peewee import DoesNotExist
from playhouse.shortcuts import model_to_dict

from piper_driver.models import *


class ProjectPresenterList(Resource):

    decorators = []

    def get(self, user):
        if user.role is UserRole.ROOT:
            query = Project.select(Project.id, Project.url)
        else:
            query = (Project.select(Project.id, Project.url, ProjectUser.role)
                     .join(ProjectUser)
                     .where(ProjectUser.user == user))

        result = []
        for project in query:
            item = model_to_dict(project)
            if user.role is not UserRole.ROOT:
                item['role'] = project.projectuser.role.value
            result.append(item)

        return result

    def post(self, user):
        if user.role is UserRole.USER:
            abort(401)


class ProjectPresenter(Resource):

    def get(self, project_id, user):
        if user.role is UserRole.ROOT:
            try:
                project = Project.get(Project.id == project_id)
            except DoesNotExist:
                abort(404)
                return

            return model_to_dict(project)

        try:
            project = (Project.select(Project.id, Project.url, ProjectUser.role)
                       .join(ProjectUser)
                       .where((ProjectUser.user == user) & (Project.id == project_id))
                       .limit(1)
                       .get())
        except DoesNotExist:
            abort(404)
            return

        item = model_to_dict(project)
        item['role'] = project.projectuser.role.value

        return item

    def put(self, project_id, user):
        pass

    def delete(self, project_id, user):
        if user.role is UserRole.ROOT:
            try:
                Project.delete(Project.id == project_id)
            except DoesNotExist:
                abort(404)
                return

            return '', 204

        try:
            project_user = ProjectUser.get(ProjectUser.user == user)
        except DoesNotExist:
            abort(404)
            return

        if project_user.role is ProjectRole.OWNER:
            try:
                Project.delete(Project.id == project_id)
            except DoesNotExist:
                abort(404)
                return
            return '', 204

        abort(400)

