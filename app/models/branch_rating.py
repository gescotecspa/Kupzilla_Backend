from app import db

class BranchRating(db.Model):
    __tablename__ = 'branch_ratings'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(1000))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.branch_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'), nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True) 
    
    branch = db.relationship('Branch', back_populates='ratings')
    user = db.relationship('User', backref='branch_ratings')
    status = db.relationship('Status', backref='branch_ratings')

    def serialize(self, first_name=None):
        return {
            'id': self.id,
            'branch_id': self.branch_id,
            'branch_name': self.branch.name if self.branch else None,
            'user_id': self.user_id,
            'user_image': self.user.image_url if self.user else None,
            'first_name': self.user.first_name if self.user else None,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat(),
            'status': self.status.serialize() if self.status else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None 
        }