import json

from aiohttp import web
from aiohttp import hdrs

import db

from models.auth import User


class RegisterView(web.View):
    async def post(self):
        from web.utils import encrypt_password, get_jwt
        data = await self.request.post()
        session = db.Session()
        user = User(username=data['username'], password=encrypt_password(data['password']))
        session.add(user)
        session.commit()
        return web.Response(body=json.dumps({"token": get_jwt(user.id)}),
                            content_type="application/json",
                            headers={hdrs.ACCESS_CONTROL_ALLOW_ORIGIN: '*'})


class LoginView(web.View):
    async def post(self):
        from web.utils import check_password, get_jwt
        data = await self.request.post()
        user = db.Session().query(User).filter_by(username=data['username']).first()
        if user and check_password(data['password'], user.password):
            return web.Response(body=json.dumps({"token": get_jwt(user.id)}),
                                content_type="application/json",
                                headers={hdrs.ACCESS_CONTROL_ALLOW_ORIGIN: '*'})
        return web.Response(body=json.dumps({'message': 'Invalid credentials'}), status=400,
                            content_type="application/json",
                            headers={hdrs.ACCESS_CONTROL_ALLOW_ORIGIN: '*'}
                            )
