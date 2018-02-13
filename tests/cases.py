from aiohttp.test_utils import AioHTTPTestCase


class BaseViewTestCase(AioHTTPTestCase):
    def get_app(self):
        from tests.app import test_app
        return test_app

    def setUp(self):
        from tests.common import Session
        super().setUp()
        self.session = Session()

    def tearDown(self):
        super().tearDown()