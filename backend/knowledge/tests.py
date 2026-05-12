"""Neo4j-backed knowledge map regression tests."""

from unittest.mock import patch, PropertyMock

from rest_framework.test import APITestCase

from courses.models import Course
from knowledge.models import KnowledgePoint
from users.models import User


class KnowledgeMapFallbackTests(APITestCase):
    """Ensure student knowledge-map endpoints expose Neo4j first with PostgreSQL fallback."""

    def setUp(self):
        """Create a published course context for knowledge-map API requests."""
        self.student = User.objects.create_user(
            username='graph_student',
            password='Test123456',
            role='student',
        )
        self.teacher = User.objects.create_user(
            username='graph_teacher',
            password='Test123456',
            role='teacher',
        )
        self.course = Course.objects.create(
            name='知识图谱课程',
            created_by=self.teacher,
        )
        self.point = KnowledgePoint.objects.create(
            course=self.course,
            name='图谱知识点',
            is_published=True,
        )
        self.client.force_authenticate(user=self.student)

    @patch('knowledge.views.neo4j_service.get_knowledge_map', return_value=None)
    @patch('knowledge.views.neo4j_service.__class__.is_available', new_callable=PropertyMock, return_value=True)
    def test_knowledge_map_should_fallback_to_postgresql_when_neo4j_graph_missing(self, *_mocks):
        """Neo4j 空图时应回退 PostgreSQL，保证学生端图谱可用。"""
        response = self.client.get(f'/api/student/knowledge-map?course_id={self.course.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['stats']['data_source'], 'postgresql')
        self.assertEqual(response.data['data']['stats']['node_count'], 1)

    @patch('knowledge.views.neo4j_service.get_knowledge_map')
    @patch('knowledge.views.neo4j_service.__class__.is_available', new_callable=PropertyMock, return_value=True)
    def test_knowledge_map_should_mark_data_source_as_neo4j(self, _available, mock_get_map):
        """Successful payloads should explicitly identify Neo4j as the data source."""
        mock_get_map.return_value = {
            'nodes': [
                {
                    'point_id': self.point.id,
                    'point_name': self.point.name,
                    'chapter': '',
                    'type': 'knowledge',
                    'level': 1,
                    'description': '',
                    'tags': '',
                    'cognitive_dimension': '',
                    'category': '',
                    'teaching_goal': '',
                }
            ],
            'edges': [
                {
                    'source': self.point.id,
                    'target': self.point.id,
                    'relation_type': 'related',
                }
            ],
        }

        response = self.client.get(f'/api/student/knowledge-map?course_id={self.course.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['stats']['data_source'], 'neo4j')
