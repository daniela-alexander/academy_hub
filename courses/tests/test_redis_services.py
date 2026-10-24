from unittest.mock import patch

from django.test import TestCase

from courses.redis_services import (
    get_academy_views,
    get_course_views,
    increment_academy_views,
    increment_course_views,
)


class CourseRedisServiceTests(TestCase):

    @patch("courses.redis_services.redis_client")
    def test_increment_course_views(self, mock_redis):
        mock_redis.incr.return_value = 1

        result = increment_course_views(1)

        self.assertEqual(result, 1)
        mock_redis.incr.assert_called_once_with("academyhub:course:1:views")

    @patch("courses.redis_services.redis_client")
    def test_get_course_views_returns_zero_if_missing(self, mock_redis):
        mock_redis.get.return_value = None

        result = get_course_views(1)

        self.assertEqual(result, 0)

    @patch("courses.redis_services.redis_client")
    def test_get_course_views_returns_value(self, mock_redis):
        mock_redis.get.return_value = "42"

        result = get_course_views(1)

        self.assertEqual(result, 42)

    @patch("courses.redis_services.redis_client")
    def test_increment_academy_views(self, mock_redis):
        mock_redis.incr.return_value = 5

        result = increment_academy_views(2)

        self.assertEqual(result, 5)
        mock_redis.incr.assert_called_once_with("academyhub:academy:2:views")

    @patch("courses.redis_services.redis_client")
    def test_get_academy_views_returns_zero_if_missing(self, mock_redis):
        mock_redis.get.return_value = None

        result = get_academy_views(2)

        self.assertEqual(result, 0)