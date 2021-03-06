import socketserver

from const import PUBLIC_URL
from server import *
from smarthome import *

if 'ngrok_tunnel' in configuration and configuration['ngrok_tunnel'] == True:
    from pyngrok import ngrok

tunnel = PUBLIC_URL


class ThreadingSimpleServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass


def startServer():
    global tunnel
    # Create tunnel if ngrok_tunnel set to true
    if 'ngrok_tunnel' in configuration and configuration['ngrok_tunnel'] is True:
        try:
            if 'ngrok_auth_token' in configuration and configuration['ngrok_auth_token'] != 'auth_token':
                ngrok.set_auth_token(configuration['ngrok_auth_token'])
            else:
                logger.info(
                    'If you use the ngrok tunnel option without account the tunnel will be terminated after 5 or 6 hours')
            public_url = ngrok.connect(configuration['port_number'])
            tunnel = public_url.replace("http", "https")
        except Exception as err:
            logger.error('Ngrok was unable to start. Error: %s is not valid' % err)
    try:
        # Create a web server and define the handler to manage the
        # incoming request
        server = ThreadingSimpleServer(('', configuration['port_number']), AogServer)
        logger.info('========')
        logger.info('Started DZGA v' + VERSION + ' server at port ' + str(configuration['port_number']))
        logger.info(' ')
        if 'userinterface' in configuration and configuration['userinterface'] is True:
            logger.info('   Visit http://localhost:' + str(
                configuration['port_number']) + '/settings to access the user interface')
        else:
            logger.info('   Configure your settings in config.yaml in Domoticz-Google-Assistant folder')
        logger.info(' ')
        logger.info('=========')
        logger.info('Visit the Actions on Google console at http://console.actions.google.com')
        logger.info('Under Develop section, replace the fulfillment URL in Actions with:')
        logger.info('   ' + tunnel + '/smarthome')
        logger.info(' ')
        logger.info('In Account linking, set the Authorization URL to:')
        logger.info('   ' + tunnel + '/oauth')
        logger.info(' ')
        logger.info('Then set the Token URL to:')
        logger.info('   ' + tunnel + '/token')
        logger.info(' ')
        logger.info('Finally press \'SAVE\' and then \'TEST\' button')
        if 'ngrok_tunnel' in configuration and configuration['ngrok_tunnel'] is True:
            logger.info('** NOTE: Ngrok assigns random urls. When server restart the server gets a new url')
        logger.info('=======')
        print("(Press CTRL+C to stop server)")
        # Sync with domoticz at startup
        try:
            getDevices()
            getSettings()
        except (ValueError, Exception):
            pass
        # Exit if running on travis
        istravis = os.environ.get('TRAVIS') == 'true'
        if istravis:
            logger.info('Travis test is finished')
            exit()
        # Wait forever for incoming http requests
        server.serve_forever()

    except (KeyboardInterrupt, SystemExit):
        print()
        logger.info('^C received, shutting down the web server')
        server.socket.close()


if __name__ == "__main__":
    # Execute only if run as a script

    for path, value in {**oauthGetMappings, **smarthomeGetMappings}.items():
        addGetMappings(path, value)

    for path, value in {**oauthPostMappings, **smarthomePostMappings}.items():
        addPostMappings(path, value)

    startServer()
