from app import db
from .user import User
# Definición de la tabla de asociación
partner_categories = db.Table('partner_categories',
    db.Column('partner_user_id', db.Integer, db.ForeignKey('partner_details.user_id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.category_id'), primary_key=True)
)

class Partner(db.Model):
    __tablename__ = 'partner_details'

    user_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.Text, nullable=True)  # No obligatorio
    contact_info = db.Column(db.String(255), nullable=True)  # No obligatorio
    business_type = db.Column(db.String(255), nullable=True) 
    categories = db.relationship('Category', secondary=partner_categories, lazy='dynamic')
    branches = db.relationship('Branch', back_populates='partner', cascade='all, delete-orphan')

    def serialize(self):

        user = None
        if self.user_id:
            user = User.query.get(self.user_id)
            if user:
                user = user.serialize()

        return {
            "user_id": self.user_id,
            "address": self.address,
            "contact_info": self.contact_info,
            "business_type": self.business_type,
            "user": user,
            "categories": [{"category_id": category.category_id, "name": category.name} for category in self.categories],
            "branches": [{"branch_id": branch.branch_id, "name": branch.name, "description": branch.description, "address": branch.address} for branch in self.branches],
        }

    def __repr__(self):
        return f"<Partner {self.user_id}: {self.address}, Contact: {self.contact_info}, Business Type: {self.business_type}>"
