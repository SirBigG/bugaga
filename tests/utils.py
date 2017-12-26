
class MockResponse(object):

    def __init__(self, content, status=200):
        self.content = content
        self.status = status
