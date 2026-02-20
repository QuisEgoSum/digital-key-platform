from sanic import Config, Sanic

from infra.sanic.ctx import AppSanicCTX

AppSanic = Sanic[Config, AppSanicCTX]
