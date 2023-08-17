from flask import jsonify,Blueprint,request,g
from datetime import datetime
from application_tracker.email_fetcher import EmailFetcher
from ..auth import check_auth_middleware
from ..db.mongo_manager import fetch_google_token
email_fetcher_blueprint = Blueprint('email_fetcher',__name__)


@email_fetcher_blueprint.before_request
def before_request_func():
    return check_auth_middleware()

@email_fetcher_blueprint.route('/fetch_emails',methods = ['POST'])
def fetch_emails():
    user_data = g.get('user', None)
    if user_data:
        user_id = user_data.get('user_id', None)
        google_token = fetch_google_token(user_id)
        # print(google_token,'gtoken')
    data = request.json
    from_date = datetime.strptime(data.get('from_date'), '%Y-%m-%d') if data.get('from_date') else None
    to_date = datetime.strptime(data.get('to_date'), '%Y-%m-%d') if data.get('to_date') else None

    # fetcher = EmailFetcher()
    return jsonify({"success": True, "from_date": from_date,"to_date":to_date})