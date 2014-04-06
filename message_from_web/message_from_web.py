from base_plugin import BasePlugin
import json
import socket
import urllib

from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from datetime import datetime


class MessageFromWeb(BasePlugin):
    """
	Receives and broadcasts messages from the Web.
	Based on "Server status query plugin v 1.1" plugin
	by ZVorgan (https://bitbucket.org/zvorgan/starrypy-server-status/)
    """
    name = "message_from_web"
    auto_activate = True

    def activate(self):
        super(MessageFromWeb, self).activate()

        try:
            self.query_port = self.config.plugin_config["query_port"]
            self.logger.info("Receiving port listen on %s.", self.query_port)
        except:
            self.query_port = 21337
            self.logger.info("Receiving port not set in config. Default port: %s.", self.query_port)

        self.listen_query();

    def listen_query(self):
        reactor.listenTCP(self.query_port, QueryFactory(self))

    def send_chat(self,data):
        now = datetime.now()
        preparsed = data.replace("GET /?a=", "");
        arraypreparsed = preparsed.split("HTTP/1.1",1)
        self.factory.broadcast("<%s> %s" % (now, urllib.unquote(arraypreparsed[0])))

class QueryFactory(Factory):
    def __init__(self, plugin_class):
        self.plugin = plugin_class;

    def buildProtocol(self, addr):
        return QueryEcho(self)

class QueryEcho(Protocol):
    def __init__(self, factory_class):
        self.factory = factory_class;

    def dataReceived(self, data):
        """
		Getting rid of favicon.ico requests:
        """
        if "/favicon.ico" not in data:
			online = self.factory.plugin.send_chat(data)
			
        self.transport.write("ok")
        self.transport.loseConnection()