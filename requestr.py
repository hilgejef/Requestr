import logging
import sys
from datetime import datetime

from flask import Flask, Response, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from credentials import DB_Credentials


# APP AND DB INITIALIZATIONS
app = Flask(__name__)

db_uri_string = 'mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}'
SQLALCHEMY_DATABASE_URI = db_uri_string.format(
        username=DB_Credentials.user,
        password=DB_Credentials.pw,
        hostname='Hilger.mysql.pythonanywhere-services.com',
        databasename='Hilger$requestr',
)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299

db = SQLAlchemy(app)


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


# IMPORTANT: Import models after app initialization, prevents import error
from models import Client, ClientRequest


# ROUTES
@app.route('/')
def index():
    return render_template('requestr.html')

@app.route('/requests')
def get_requests():
    # Returns list of requests represented as dictionaries
    requests = ClientRequest.query.all()

    rlist = [dict(id=r.id,
                  title=r.title,
                  description=r.description,
                  target=r.target.strftime('%m-%d-%Y'),
                  area=r.area,
                  client=r.client,
                  priority=r.priority) for r in requests]

    return jsonify(requests=rlist)

@app.route('/clients')
def get_clients():
    # Returns list of clients represented as dictionaries
    clients = Client.query.all()

    clist = [dict(name=c.name) for c in clients]

    return jsonify(clients=clist)

@app.route('/requests/new', methods=['POST'])
def create_request():
    # Creates a feature request in the database
    try:
        logging.info(request.json)
        pri = int(request.json['priority'])
        cli = request.json['client']

        # Priority/client combinations are unique, check if one already exists
        cr_violation = ClientRequest.query.filter_by(priority=pri, client=cli).first()
        if (cr_violation):
            # If one does exist, shift up requests >= priority by 1 until space is made
            shift_up = [cr_violation]
            for cr in db.session.query(ClientRequest).filter(
                    ClientRequest.priority > pri,
                    ClientRequest.client==cli).order_by(ClientRequest.priority.asc()):
                if cr.priority == shift_up[-1].priority + 1:
                    shift_up.append(cr)
                else:
                    break
            for su in reversed(shift_up):
                su.priority += 1
                db.session.add(su)
                db.session.commit()

        req = ClientRequest(title=request.json['title'],
                            description=request.json['description'],
                            target=datetime.strptime(request.json['target'], '%Y-%m-%d'),
                            area=request.json['area'],
                            client=cli,
                            priority=pri)

        db.session.add(req)
        db.session.commit()

        return jsonify(dict(id=req.id,
                            title=req.title,
                            description=req.description,
                            target=req.target,
                            area=req.area,
                            client=req.client,
                            priority=req.priority))
    except:
        # Simple try/except with logger, simplified for this exercise
        logging.exception('Failed to create request')
        return Response({'success': False}, status=400, mimetype='application/json')

@app.route('/requests/delete', methods=['POST'])
def delete_request():
    # Deletes a request in the database, based on ID
    try:
        req = ClientRequest.query.get(int(request.json['id']))

        db.session.delete(req)
        db.session.commit()

        return jsonify({'success': True})

    except:
        # Another simple try/except with logger
        logging.exception('Failed to delete request')
        return Response({'success' : False}, status=400, mimetype='application/json')