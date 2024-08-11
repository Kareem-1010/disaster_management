from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app,jsonify
from flask_login import login_user, current_user, logout_user, login_required
from extensions import db
from models import User, Resource, Donation
from forms import RegistrationForm, LoginForm, ResourceForm, DonationForm
import json
from geopy.distance import geodesic
import random

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    return render_template('index.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('main.login'))  # Correct endpoint
    return render_template('register.html', title='Register', form=form)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))  # Correct endpoint
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    resources = Resource.query.filter_by(user_id=current_user.id)
    donations = Donation.query.filter_by(user_id=current_user.id)
    return render_template('dashboard.html', title='Dashboard', resources=resources, donations=donations)

@main_bp.route('/resource_map', methods=['GET', 'POST'])
def resource_map():
    form = ResourceForm()
    if form.validate_on_submit():
        resource = Resource(
            name=form.name.data, 
            description=form.description.data, 
            latitude=form.latitude.data, 
            longitude=form.longitude.data, 
            user_id=current_user.id
        )
        db.session.add(resource)
        db.session.commit()
        flash('Resource added successfully!', 'success')
        return redirect(url_for('main.resource_map'))

    resources = Resource.query.all()
    resources_dict = [resource.to_dict() for resource in resources]
    resources_json = json.dumps(resources_dict)
    resources_json = [{'name': r.name, 'description': r.description, 'latitude': r.latitude, 'longitude': r.longitude} for r in resources]
    return render_template('resource_map.html', form=form,resources_json=resources_json, api_key=current_app.config['GOOGLE_MAPS_API_KEY'])

@main_bp.route('/donate', methods=['GET', 'POST'])
@login_required
def donate():
    form = DonationForm()
    if form.validate_on_submit():
        donation = Donation(amount=form.amount.data, user_id=current_user.id)
        db.session.add(donation)
        db.session.commit()
        flash('Thank you for your donation!', 'success')
        return redirect(url_for('main.dashboard'))  # Correct endpoint
    return render_template('donate.html', title='Donate', form=form)

@main_bp.route('/prediction')
def prediction():
    # Example: Check if any resources are near a disaster-prone area
    resources = Resource.query.all()
    prediction_result = "No disaster predicted in the near future."

    for resource in resources:
        if is_disaster_prone_area(resource.latitude, resource.longitude):
            prediction_result = f"Disaster predicted near {resource.name}."
            break

    return render_template('prediction.html', prediction=prediction_result)

def is_disaster_prone_area(lat, lng):
    # Simplistic check - Replace with actual prediction logic
    disaster_prone_areas = [
        {'lat': 34.0522, 'lng': -118.2437},  # Example: Los Angeles
        {'lat': 37.7749, 'lng': -122.4194}   # Example: San Francisco
    ]
    
    for area in disaster_prone_areas:
        if abs(lat - area['lat']) < 1 and abs(lng - area['lng']) < 1:
            return True
    return False


@main_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))  # Correct endpoint