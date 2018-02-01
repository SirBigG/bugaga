from tests.factories import CategoryFactory

from aiohttp.test_utils import AioHTTPTestCase


class ClassifierListViewTest(AioHTTPTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    async def test_list_response(self):
        category = CategoryFactory()
        response = await self.client.request('GET', '/api/classifiers/')
        assert response.status == 200
        data = await response.json()
        assert len(data) == 1
        assert data[0]['title'] == category.title
