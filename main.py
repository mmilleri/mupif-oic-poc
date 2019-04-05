import json

from bottle import run, template, request, route, redirect, response
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError, KeycloakGetError


def main():
    run(host='localhost', port=8080)


@route('/')
def get_slash():
    if is_authorization_redirect():
        code = request.query['code']
        session_id = request.query['session_state']
        token = keycloak_openid.token(grant_type="authorization_code", code=code, redirect_uri="http://localhost:8080")

        save_session(session_id, token)
        redirect('/')

    elif is_user_logged():
        try:
            token = sessions[request.get_cookie('session_id')]
            access_token = token['access_token']
        except KeyError:
            response.delete_cookie('session_id')
            return redirect('/')

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
    token = sessions[request.get_cookie('session_id')]
    refresh_token = token['refresh_token']
    keycloak_openid.logout(refresh_token)

    clear_session()
    redirect('/')


def is_authorization_redirect():
    return 'code' in request.query.keys()


def is_user_logged():
    return request.get_cookie('session_id')


def refresh_tokens():
    session_id = request.get_cookie('session_id')
    token = sessions[session_id]
    refresh_token = token['refresh_token']

    try:
        new_token = keycloak_openid.refresh_token(refresh_token)
    except KeycloakGetError:
        print('Token expired. Login again.')
        clear_session()
        return redirect('/')

    save_session(session_id, new_token)
    print('Token refreshed')


def save_session(session_id, token):
    sessions[session_id] = token
    response.set_cookie('session_id', session_id)


def clear_session():
    response.delete_cookie('session_id')
    del sessions[request.get_cookie('session_id')]


if __name__ == '__main__':
    sessions = {}
    keycloak_conf = json.loads(open('keycloak.json').read())
    keycloak_openid = KeycloakOpenID(server_url=keycloak_conf['auth-server-url'] + "/",
                                     realm_name=keycloak_conf['realm'],
                                     client_id=keycloak_conf['resource'],
                                     client_secret_key=keycloak_conf['credentials']['secret'])
    login_url = keycloak_openid.auth_url("http://localhost:8080")
    main()
