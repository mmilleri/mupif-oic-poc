# mupic-oic-poc
Proof of concept OpenID authentication with Keycloak for mupif

## Python dependencies
- Install *pip*

  ```
  python3 -m pip install --user --upgrade pip
  ```

- Install *virtualenv*

  ```
  python3 -m pip install --user virtualenv
  ```

- Activate the virtualenv

  ```
  source env/bin/activate
  ```

- Install dependencies

  ```
  pip install -r requirements.txt
  ```
  
## Additional dependencies
- A running *Keycloak* authentication server
- The `keycloak.json` configuration file for that server in `mupic-oic-poc` directory
  
## How to launch
- Activate the virtualenv

  ```
  source env/bin/activate
  ```
  
- Run the script

  ```
  python main.py
  ```
