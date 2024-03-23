from unittest import TestCase

from slack.domain.task.task import Task
from slack.infrastructure.task.request.update_task_request import UpdateTaskRequest


class TestUpdateTaskRequest(TestCase):
    def test_from_entity(self):
        entity=Task.test_instance()
        entity.status="Done"
        actual = UpdateTaskRequest.from_entity(entity)
        self.assertEqual(actual.__dict__, {"status": "Done"})
