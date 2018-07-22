from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from datetime import datetime

user_role_assoc = db.Table("user_role_assoc",
                    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
                    db.Column("role_id", db.Integer, db.ForeignKey("roles.id")))

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about = db.Column(db.String(1000))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    
    roles = db.relationship("Role", secondary=user_role_assoc, backref="users")

    def has_role(self, roleId):
        role = Role.query.get(roleId)

        return role in self.roles

    def has_admin_role(self):
        return self.has_role(1)

    def has_map_role(self):
        return self.has_role(2)

    def has_event_role(self):
        return self.has_role(3)

    def has_special_role(self):
        return self.has_role(4)

    def is_map_admin(self):
        return self.has_admin_role() or self.has_map_role()

    def is_event_admin(self):
        return self.has_admin_role() or self.has_event_role()

    def has_access_to_some_settings(self):
        return self.has_admin_role() or self.has_map_role()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(256))

class GeneralSetting(db.Model):
    __tablename__ = "general_settings"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))

class MapNodeType(db.Model):
    __tablename__ = "map_node_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(256))
    icon_file = db.Column(db.String(64))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))