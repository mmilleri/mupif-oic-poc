import json

from bottle import run, template, request, route, redirect
from keycloak import KeycloakOpenID


def main():
    run(host='localhost', port=8080)


@route('/')
def get_slash():
    if 'code' in request.query.keys():
        code = request.query['code']

        token = keycloak_openid.token(grant_type="authorization_code", code=code, redirect_uri="http://localhost:8080")
        global_variables['token'] = token

        userinfo = keycloak_openid.userinfo(token['access_token'])
        username = userinfo['preferred_username']
        email = userinfo['email'] if 'email' in userinfo.keys() else ''
        given_name = userinfo['given_name'] if 'given_name' in userinfo.keys() else ''
        family_name = userinfo['family_name'] if 'family_name' in userinfo.keys() else ''

        return template('logged.html', name=username, email=email, given_name=given_name, family_name=family_name)
    else:
        return template('main.html', login_url=login_url)


@route('/logout')
def logout():
    token = global_variables['token']
    keycloak_openid.logout(token['refresh_token'])
    redirect('/')


if __name__ == '__main__':
    global_variables = {}
    keycloak_conf = json.loads(open('keycloak.json').read())
    keycloak_openid = KeycloakOpenID(server_url=keycloak_conf['auth-server-url'] + "/",
                                     realm_name=keycloak_conf['realm'],
                                     client_id=keycloak_conf['resource'],
                                     client_secret_key=keycloak_conf['credentials']['secret'])
    login_url = keycloak_openid.auth_url("http://localhost:8080")
    main()
