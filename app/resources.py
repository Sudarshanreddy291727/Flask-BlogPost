from flask_restful import Resource, reqparse
from app.models import db, Task
from flask_login import current_user, login_required

task_parser = reqparse.RequestParser()
task_parser.add_argument('title', type=str, required=True, help='Title cannot be blank')

class TaskResource(Resource):
    @login_required
    def get(self, task_id=None):
        if task_id:
            task = Task.query.get(task_id)
            if task and task.author == current_user:
                return {'id': task.id, 'title': task.title, 'date_created': task.date_created}, 200
            return {'message': 'Task not found or not authorized'}, 404
        tasks = Task.query.filter_by(author=current_user).all()
        return [{'id': task.id, 'title': task.title, 'date_created': task.date_created} for task in tasks], 200

    @login_required
    def post(self):
        args = task_parser.parse_args()
        new_task = Task(title=args['title'], author=current_user)
        db.session.add(new_task)
        db.session.commit()
        return {'message': 'Task created', 'task': {'id': new_task.id, 'title': new_task.title, 'date_created': new_task.date_created}}, 201

    @login_required
    def put(self, task_id):
        args = task_parser.parse_args()
        task = Task.query.get(task_id)
        if task and task.author == current_user:
            task.title = args['title']
            db.session.commit()
            return {'message': 'Task updated', 'task': {'id': task.id, 'title': task.title, 'date_created': task.date_created}}, 200
        return {'message': 'Task not found or not authorized'}, 404

    @login_required
    def delete(self, task_id):
        task = Task.query.get(task_id)
        if task and task.author == current_user:
            db.session.delete(task)
            db.session.commit()
            return {'message': 'Task deleted'}, 200
        return {'message': 'Task not found or not authorized'}, 404
