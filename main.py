import json

from bottle import run, template, request, route, redirect, response
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError


def main():
    run(host='localhost', port=8080)


@route('/')
def get_slash():
    if is_authorization_redirect():
        code = request.query['code']
        token = keycloak_openid.token(grant_type="authorization_code", code=code, redirect_uri="http://localhost:8080")
        set_cookies_from_token(token)

        redirect('/')

    elif user_is_logged():
        access_token = request.get_cookie('access_token')

        try:
            userinfo = keycloak_openid.userinfo(access_token)
            username = userinfo['preferred_username']
            email = userinfo['email'] if 'email' in userinfo.keys() else ''
            given_name = userinfo['given_name'] if 'given_name' in userinfo.keys() else ''
            family_name = userinfo['family_name'] if 'family_name' in userinfo.keys() else ''
            return template('logged.html', name=username, email=email, given_name=given_name, family_name=family_name)
        except KeycloakAuthenticationError:
            refresh_tokens()
            redirect('/')
    else:
        return template('main.html', login_url=login_url)


@route('/logout')
def logout():
    refresh_token = request.get_cookie('refresh_token')
    keycloak_openid.logout(refresh_token)
    clear_cookies()
    redirect('/')


def is_authorization_redirect():
    return 'code' in request.query.keys()


def user_is_logged():
    return request.get_cookie('access_token')


def refresh_tokens():
    refresh_token = request.get_cookie('refresh_token')
    token = keycloak_openid.refresh_token(refresh_token)
    set_cookies_from_token(token)


def set_cookies_from_token(token):
    response.set_cookie('access_token', token['access_token'], max_age=token['expires_in'])
    response.set_cookie('refresh_token', token['refresh_token'], max_age=token['refresh_expires_in'])


def clear_cookies():
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')


if __name__ == '__main__':
    keycloak_conf = json.loads(open('keycloak.json').read())
    keycloak_openid = KeycloakOpenID(server_url=keycloak_conf['auth-server-url'] + "/",
                                     realm_name=keycloak_conf['realm'],
                                     client_id=keycloak_conf['resource'],
                                     client_secret_key=keycloak_conf['credentials']['secret'])
    login_url = keycloak_openid.auth_url("http://localhost:8080")
    main()
