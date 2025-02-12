# Copyright (c) Istituto Nazionale di Fisica Nucleare (INFN). 2020-2024
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

### DB SETTINGS
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://slat:slat@localhost:3306/slat"
SQLALCHEMY_TRACK_MODIFICATIONS = "False"

#### AUTH SETTINGS
IAM_BASE_URL="https://iam.example.org/"
IAM_CLIENT_ID="MY_CLIENT_ID"
IAM_CLIENT_SECRET="MY_CLIENT_SECRET"
EGI_AAI_BASE_URL="https://https://aai-dev.egi.eu/oidc/"
EGI_AAI_CLIENT_ID=""
EGI_AAI_CLIENT_SECRET=""

TRUSTED_OIDC_IDP_LIST = [ { 'iss': 'https://iam.example.org/', 'type': 'indigoiam' } ]
FLAAT_VERIFY_JWT = False
FLAAT_VERIFY_TLS = True
FLAAT_ISS = ""
FLAAT_REQUEST_TIMEOUT = 60

### ROLES
SLAT_ADMIN_GROUP = "slat-admin"

#### APP SETTINGS
LOG_LEVEL = "DEBUG"
USER_ENABLE_EMAIL = False
CMDB_URL = "https://cmdb.example.org"
CMDB_CA_CERT = None
