from requestr import db
from models import Client

if __name__ == "__main__":
    db.create_all()

    client_A = Client("A")
    client_B = Client("B")
    client_C = Client("C")

    db.session.add(client_A)
    db.session.add(client_B)
    db.session.add(client_C)

    db.session.commit()