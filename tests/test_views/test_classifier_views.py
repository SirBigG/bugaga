from tests.factories import CategoryFactory, UserFactory
from tests.cases import BaseViewTestCase

from aiohttp.test_utils import unittest_run_loop

from models.auth import User


class ClassifierListViewTest(BaseViewTestCase):

    def setUp(self):
        from models.category import Category
        super().setUp()
        self.session.query(Category).delete()
        self.session.commit()

    # @unittest_run_loop
    # async def test_list_response(self):
    #     category = CategoryFactory()
    #     response = await self.client.request('GET', '/api/classifiers/')
    #     assert response.status == 200
    #     data = await response.json()
    #     assert len(data) == 1
    #     assert data[0]['title'] == category.title

    # @unittest_run_loop
    # async def test_registration(self):
    #     response = await self.client.request('POST', '/api/registration/', data={'username': 'regusername',
    #                                                                              'password': '12345'})
    #     assert response.status == 200
    #     assert self.session.query(User).filter_by(username='regusername').first()
    #     data = await response.json()
    #     print(data)
    #     assert 'token' in data

    # @unittest_run_loop
    # async def test_invalid_login(self):
    #     response = await self.client.request('POST', '/api/login/', data={'username': 'loginusername',
    #                                                                       'password': '12345'})
    #     assert response.status == 400
    #     data = await response.json()
    #     assert 'message' in data

    @unittest_run_loop
    async def test_valid_login(self):
        from web.utils import encrypt_password
        UserFactory(username='loginusername', password=encrypt_password('12345'))
        response = await self.client.request('POST', '/api/login/', data={'username': 'loginusername',
                                                                          'password': '12345'})
        assert response.status == 200
        data = await response.json()
        assert 'token' in data