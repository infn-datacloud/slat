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
from werkzeug.exceptions import Unauthorized, BadRequest, InternalServerError
from flaat import access_tokens
from app.extensions import cmdb_client, flaat
from app import decoders, models, db
from flask import current_app as app, Blueprint, request, render_template, make_response
from datetime import datetime, timezone
from app.models import SlaStatusTypes

rest_bp = Blueprint('rest_bp', __name__,
                           template_folder='templates',
                           static_folder='static')


class TokenDecoder:
    def get_groups(self, request):
        access_token = access_tokens.get_access_token_from_request(request)
        #issuer = issuertools.find_issuer_config_in_at(access_token)
        #info = flaat.get_info_thats_in_at(access_token)
        info = flaat.get_info_from_userinfo_endpoints(access_token)
        iss = access_token['iss']

        idp = next(filter(lambda x: x['iss']==iss, app.config.get('TRUSTED_OIDC_IDP_LIST')))

        if 'client_id' in idp and 'client_secret' in idp:
            flaat.set_client_id(idp['client_id'])
            flaat.set_client_secret(idp['client_secret'])
            info = flaat.get_info_from_introspection_endpoints(access_token)
        decoder = decoders.factory.get_decoder(idp['type'])
        return decoder.get_groups(info)


@rest_bp.route("/slam/preferences/<path:group>", methods=["GET"])
@flaat.is_authenticated()
def get_by_group(group=None):
    
    # Query the SLAs based on the provided group
    try:
        slas = []
        if group:
            current_date = datetime.now(timezone.utc)
            slas = db.session.query(models.Sla).filter(
                models.Sla.customer == group,
                models.Sla.status != SlaStatusTypes.disabled,  # Exclude disabled SLAs
                models.Sla.end_date > current_date  # Exclude SLAs that have expired based on date
            ).all()
            app.logger.debug(f"Computed SLAs for group {group}: {slas}")
        else:
            raise BadRequest(description="Group parameter is required")
    except Exception as e:
        app.logger.error(f"Database query failed: {str(e)}")
        raise InternalServerError(description="Failed to retrieve SLAs")

    # Generate the response
    response = make_response(render_template('slas.json', slas=slas, customer=group))
    response.headers['Content-Type'] = 'application/json'
    return response

