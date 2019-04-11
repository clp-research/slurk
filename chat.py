#!/bin/env python
from app import create_app, socketio
import configparser
from gevent import monkey

monkey.patch_all(subprocess=True)


app = create_app()

config = configparser.ConfigParser()
config.read("config.ini")

if __name__ == '__main__':
    if config['ssl']['enabled'] == 'yes':
        import ssl
        from wsgiserver import WSGIServer

        ctx = ssl.SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)
        ctx.load_cert_chain(config['ssl']['certificate'], config['ssl']['key'])

        http_server = WSGIServer(
            (config['server']['host'], config['server']['port']),
            app,
            certfile=config['ssl']['certificate'],
            keyfile=config['ssl']['key']
        )
        http_server.serve_forever()
        socketio.run(app, config['server']['host'], int(
            config['server']['port']), ssl_context=ctx)
    else:
        socketio.run(app, config['server']['host'],
                     int(config['server']['port']))
