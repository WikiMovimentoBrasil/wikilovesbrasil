import ast
from db import db

monument_state = db.Table('monument_state',
                          db.Column('monument_id', db.String(50), db.ForeignKey('monuments.item'), primary_key=True),
                          db.Column('state_id', db.String(50), db.ForeignKey('state.item'), primary_key=True))


class Monument(db.Model):
    __tablename__ = 'monuments'

    item = db.Column(db.String(100), unique=True, primary_key=True)
    coord_lat = db.Column(db.Float, nullable=False)
    coord_lon = db.Column(db.Float, nullable=False)
    label = db.Column(db.String(500), nullable=False)
    label_en = db.Column(db.String(500), nullable=False)
    descr = db.Column(db.String(500), nullable=False)
    descr_en = db.Column(db.String(500), nullable=False)
    imagem = db.Column(db.String(500), nullable=True)
    types = db.Column(db.String(500), nullable=False)
    p18 = db.Column(db.String(500), nullable=True)
    p3451 = db.Column(db.String(500), nullable=True)
    p5775 = db.Column(db.String(500), nullable=True)
    p8592 = db.Column(db.String(500), nullable=True)
    p9721 = db.Column(db.String(500), nullable=True)
    p4291 = db.Column(db.String(500), nullable=True)
    p8517 = db.Column(db.String(500), nullable=True)
    p1801 = db.Column(db.String(500), nullable=True)
    p1766 = db.Column(db.String(500), nullable=True)
    p9906 = db.Column(db.String(500), nullable=True)
    p3311 = db.Column(db.String(500), nullable=True)
    state = db.relationship('State', secondary=monument_state, backref='monuments', lazy='dynamic')

    def to_dict(self):
        return {
            'item': self.item,
            'coord': [self.coord_lat, self.coord_lon],
            'imagem': self.imagem or "No-image.png",
            'label': self.label,
            'types': ast.literal_eval(self.types) or [],
            'p18': self.p18 or "",
            'p1766': self.p1766 or "",
            'p1801': self.p1801 or "",
            'p3311': self.p3311 or "",
            'p3451': self.p3451 or "",
            'p4291': self.p4291 or "",
            'p5775': self.p5775 or "",
            'p8517': self.p8517 or "",
            'p8592': self.p8592 or "",
            'p9721': self.p9721 or "",
            'p9906': self.p9906 or "",
        }

    def __repr__(self):
        if self.label:
            return self.label
        else:
            return self.label_en


class State(db.Model):
    __tablename__ = 'state'

    item = db.Column(db.String(100), unique=True, primary_key=True)
    label = db.Column(db.String(500), nullable=False)
    label_en = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        if self.label:
            return self.label
        else:
            return self.label_en
