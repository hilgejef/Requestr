from requestr import db

class ClientRequest(db.Model):
    __tablename__ = 'requests'

    __table_args__ = (db.UniqueConstraint('client', 'priority', name='_client_priority'),)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(480), nullable=False)
    target = db.Column(db.DateTime, nullable=False)
    area = db.Column(db.String(120), nullable=False)

    client = db.Column(db.String(80), db.ForeignKey('clients.name'), nullable=False)
    priority = db.Column(db.Integer, nullable=False)

    def __init__(self, title, description, target, area, client, priority):
        self.title = title
        self.description = description
        self.target = target
        self.area = area
        self.client = client
        self.priority = priority

    def __repr__(self):
        return '\n'.join('ID: ' + self.id,
                         'Title: ' + self.title,
                         'Description: ' + self.description,
                         'Target Date: ' + self.target,
                         'Product Area: ' + self.area,
                         'Client: ' + self.client,
                         'Priority: ' + self.priority)

class Client(db.Model):
    __tablename__ = 'clients'

    name = db.Column(db.String(80), primary_key=True)

    requests = db.relationship('ClientRequest', backref='_client', lazy=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Name: ' + self.name