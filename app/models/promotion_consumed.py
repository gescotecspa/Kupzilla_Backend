from app import db
from datetime import datetime

class PromotionConsumed(db.Model):
    __tablename__ = 'promotion_consumed'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    promotion_id = db.Column(db.Integer, db.ForeignKey('promotions.promotion_id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'), nullable=False)
    quantity_consumed = db.Column(db.Integer, nullable=False, default=1)
    amount_consumed = db.Column(db.Float, nullable=True)
    consumption_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    payment_method = db.Column(db.String(50), nullable=True) 

    user = db.relationship('User', backref='promotions_consumed')
    promotion = db.relationship('Promotion', backref='promotions_consumed')
    status = db.relationship('Status', backref=db.backref('promotions_consumed'))

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'promotion_id': self.promotion_id,
            'status': self.status.serialize() if self.status else None,
            'quantity_consumed': self.quantity_consumed,
            'amount_consumed': self.amount_consumed,
            'consumption_date': self.consumption_date.isoformat() if self.consumption_date else None,
            'description': self.description,
            'payment_method': self.payment_method
        }
