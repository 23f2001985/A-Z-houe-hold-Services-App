from .database import db
from datetime import datetime

class Admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.String, primary_key=True, unique=True)
    password = db.Column(db.String, nullable=False)

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.String, primary_key=True, unique=True)
    password = db.Column(db.String, nullable=False)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.String, primary_key=True)  
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)  
    password = db.Column(db.String, nullable=False)  
    full_name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    pincode = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=True)  
    admin_status = db.Column(db.String, nullable=True)
    rating2 = db.Column(db.Float, nullable=True, default='0.0')   

class ServiceProvider(db.Model):
    __tablename__ = 'service_provider'
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False) 
    password = db.Column(db.String, nullable=False)  
    full_name = db.Column(db.String, nullable=False)
    service_name = db.Column(db.String, nullable=False)
    experience_years = db.Column(db.Integer, nullable=False)
    pincode = db.Column(db.String, nullable=False)
    base_price = db.Column(db.Float, nullable=False)  
    rating = db.Column(db.Float, nullable=True) 
    request_time = db.Column(db.DateTime, default=None)
    admin_approval = db.Column(db.String, nullable=True, default='not approved')
    phone_number = db.Column(db.String, nullable=True)  
    job_description = db.Column(db.String, nullable=True)  

class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.String, primary_key=True, )
    service_name = db.Column(db.String, nullable=False, unique=True)
    base_price = db.Column(db.Float, nullable=True)
    service_description = db.Column(db.String, nullable=True)  

class ServiceRequests(db.Model):
    __tablename__ = 'service_requests'
    id = db.Column(db.String, primary_key=True)
    serv_name = db.Column(db.String, nullable=True)
    customer_email = db.Column(db.String(120), nullable=False)
    provider_email = db.Column(db.String(120), nullable=True)
    service_request_time = db.Column(db.DateTime, default=None)
    service2_status = db.Column(db.String, nullable=True)
    service_close_time = db.Column(db.DateTime, nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    remarks = db.Column(db.String(500), nullable=True)
    
