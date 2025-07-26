from flask import Flask, request, render_template, flash, redirect, url_for, current_app as app , Response
from application.models import Customer, ServiceProvider , ServiceRequests , Service
from application.database import db
from application import database
from application.models import User, Customer, ServiceProvider , Admin , Service 
from datetime import datetime
from flask import session

with app.app_context():
    database.db.create_all()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        admin = Admin.query.filter_by(admin_id=email, password=password).first()
        if admin:
            return redirect(url_for("admin_dashboard", user_id=email))
        user = User.query.filter_by(user_id=email).first()
        if not user:
            flash("New user, please sign up!",'success')
            return redirect(url_for("home"))
        customer = Customer.query.filter_by(user_id=email, password=password).first()
        if customer:
            if customer.admin_status == 'blocked':
                flash("You have been blocked by the admin and cannot log in.", 'danger')
                return redirect(url_for("home"))
            return redirect(url_for("customer_dashboard", user_id=email))
        service_provider = ServiceProvider.query.filter_by(user_id=email, password=password).first()
        if service_provider:
            if service_provider.admin_approval == 'blocked':
                flash("You have been blocked by the admin and cannot log in.", 'danger')
                return redirect(url_for("home"))
            return redirect(url_for("professional_dashboard", user_id=email))
        flash("Invalid email or password! Please try again.",'danger')
        return redirect(url_for("home"))

    return render_template("home.html")

@app.route("/customer_signup", methods=["GET", "POST"])
def customer_signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        full_name = request.form.get("full_name")
        address = request.form.get("address")
        pincode = request.form.get("pincode")
        phone_number = request.form.get("phone_number")  
        existing_user = User.query.filter_by(user_id=email).first()
        if existing_user:
            flash("This email is already registered!",'warning')
            return redirect(url_for("home"))
        initials = "".join([name[0].upper() for name in full_name.split()])
        timestamp = datetime.utcnow().strftime("%d%m%H%S")  
        customer_id = f"C{timestamp}{initials}"
        new_user = User(user_id=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        new_customer = Customer(
            id=customer_id,  
            user_id=email,
            password=password,
            full_name=full_name,
            address=address,
            pincode=pincode,
            phone_number=phone_number,  
        )
        db.session.add(new_customer)
        db.session.commit()
        flash("Customer registration successful!",'success')
        return redirect(url_for("home"))
    return render_template("customer_signup.html")

@app.route("/professional_signup", methods=["GET", "POST"])
def professional_signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        full_name = request.form.get("full_name")
        service_name = request.form.get("service_name")
        experience = int(request.form.get("experience"))
        pincode = request.form.get("pincode")
        phone_number = request.form.get("phone_number")  
        existing_user = User.query.filter_by(user_id=email).first()
        if existing_user:
            flash("This email is already registered!",'warning')
            return redirect(url_for("home"))
        service = Service.query.filter_by(service_name=service_name).first()
        if not service:
            flash("Invalid service selected. Please try again.")
            return redirect(url_for("professional_signup"))
        initials = "".join([name[0].upper() for name in full_name.split()])
        timestamp = datetime.utcnow().strftime("%d%m%H%S")  
        professional_id = f"P{timestamp}{initials}"
        new_user = User(user_id=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        new_professional = ServiceProvider(
            id=professional_id, 
            user_id=email,
            full_name=full_name,
            password=password,
            service_name=service_name,
            experience_years=experience,
            pincode=pincode,
            phone_number=phone_number,  
            rating=0, 
            base_price=service.base_price,
            job_description=service.service_description 
        )
        db.session.add(new_professional)
        db.session.commit()
        flash("Professional registration successful!",'success')
        return redirect(url_for("home"))
    services = Service.query.all()
    return render_template("professional_signup.html", services=services)

@app.route("/admin_dashboard/<user_id>")
def admin_dashboard(user_id):
    cus=Customer.query.all()
    services = Service.query.all()
    professionals = ServiceProvider.query.all()
    service_requests = []
    for request in ServiceRequests.query.all():
        provider = ServiceProvider.query.filter_by(user_id=request.provider_email).first()
        service_requests.append({
            "id": request.id,
            "customer_email": request.customer_email,
            "professional_name": provider.full_name if provider else "N/A",
            "requested_date": request.service_request_time.strftime('%Y-%m-%d %H:%M:%S') if request.service_request_time else "N/A",
            "status": request.service2_status
        })
    return render_template("admin_dashboard.html",user_id=user_id,services=services,professionals=professionals,service_requests=service_requests,cus=cus)

@app.route("/reject_professional/<professional_id>/<user_id>", methods=["POST"])
def reject_professional(professional_id, user_id):
    professional = ServiceProvider.query.get(professional_id)
    if professional:
        professional.admin_approval = "rejected"
        db.session.commit()
        flash(f"Professional {professional.full_name} has been rejected.",'warning')
    else:
        flash("Professional not found.", "danger")
    return redirect(url_for("admin_dashboard", user_id=user_id))

@app.route("/approve_professional/<professional_id>/<user_id>", methods=["POST"])
def approve_professional(professional_id, user_id):
    professional = ServiceProvider.query.get(professional_id)
    if professional:
        professional.admin_approval = "approved"
        db.session.commit()
        flash(f"Professional {professional.full_name} has been approved.",'success')
    return redirect(url_for("admin_dashboard", user_id=user_id))

@app.route("/add_services/<user_id>")
def add_services(user_id):
    return render_template("add_services.html", user_id=user_id)
@app.route("/submit_service/<user_id>", methods=["POST"])
def submit_service(user_id):
    service_id = request.form.get("service_id")
    service_name = request.form.get("service_name")
    base_price = request.form.get("base_price")
    service_description = request.form.get("work_description") 
    existing_service = Service.query.filter(
        (Service.id == service_id) | (Service.service_name == service_name)
    ).first()
    if existing_service:
        flash("Service ID or Service Name already exists!")
        return redirect(url_for("add_services", user_id=user_id))
    new_service = Service(
        id=service_id,
        service_name=service_name,
        base_price=base_price,
        service_description=service_description, 
    )
    db.session.add(new_service)
    db.session.commit()
    flash("Service added successfully!",'success')
    return redirect(url_for("admin_dashboard", user_id=user_id))

@app.route("/delete_service/<user_id>/<service_id>", methods=["POST"])
def delete_service(user_id, service_id):
    service_to_delete = Service.query.get(service_id)
    if service_to_delete:
        db.session.delete(service_to_delete)
        db.session.commit()
        flash("Service deleted successfully!",'warning')
    else:
        flash("Service not found!")
    return redirect(url_for("admin_dashboard", user_id=user_id))

@app.route("/admin_search/<user_id>", methods=["GET", "POST"])
def admin_search(user_id):
    search_term = request.form.get("search_term", "").strip() if request.method == "POST" else ""
    service_providers = []
    service_requests = []
    if search_term:
        service_providers = ServiceProvider.query.filter(
            (ServiceProvider.full_name.ilike(f"%{search_term}%")) |
            (ServiceProvider.service_name.ilike(f"%{search_term}%")) |
            (ServiceProvider.pincode.ilike(f"%{search_term}%")) |
            (ServiceProvider.admin_approval.ilike(f"%{search_term}%"))
        ).all()
        all_requests = ServiceRequests.query.all()
        for req in all_requests:
            provider = ServiceProvider.query.filter_by(user_id=req.provider_email).first()
            if (
                search_term.lower() in (provider.full_name.lower() if provider else "") or
                search_term.lower() in (provider.service_name.lower() if provider else "") or
                search_term.lower() in req.customer_email.lower() or
                search_term.lower() in req.service2_status.lower()
            ):
                service_requests.append({
                    "id": req.id,
                    "customer_email": req.customer_email,
                    "professional_name": provider.full_name if provider else "N/A",
                    "requested_date": req.service_request_time.strftime('%Y-%m-%d %H:%M:%S') if req.service_request_time else "N/A",
                    "status": req.service2_status,
                })
    return render_template("admin_search.html",user_id=user_id,service_providers=service_providers,service_requests=service_requests)

@app.route('/edit_service/<service_id>/<user_id>', methods=['GET'])
def edit_service(service_id,user_id):
    service = Service.query.filter_by(id=service_id).first()    
    if service:
        return render_template('edit_service.html', service=service, user_id=user_id)
    else:
        return "Service not found"
@app.route('/update_service/<service_id>/<user_id>', methods=['POST'])
def update_service(service_id, user_id):
    service = Service.query.filter_by(id=service_id).first()
    if service:
        service_name = request.form['service_name']
        base_price = request.form['base_price']
        work_description = request.form['work_description'] 
        service.service_name = service_name
        service.base_price = base_price
        service.work_description = work_description  
        db.session.commit()
        return redirect(url_for('admin_dashboard', user_id=user_id))
    else:
        return "Service not found"
    
@app.route("/admin_professional_details/<professional_id>/<user_id>", methods=["GET", "POST"])
def admin_professional_details(professional_id, user_id):
    professional = ServiceProvider.query.filter_by(id=professional_id).first()
    if not professional:
        flash("Professional not found.", "danger")
        return redirect(url_for('admin_dashboard', user_id=user_id))
    return render_template("ad_prof_det.html", professional=professional, user_id=user_id)

@app.route("/block_professional/<professional_id>/<user_id>", methods=["POST"])
def block_professional(professional_id,user_id):
    professional = ServiceProvider.query.filter_by(id=professional_id).first()
    if not professional:
        flash("Professional not found.", "danger")
        return redirect(url_for('admin_dashboard', user_id=user_id))
    professional.admin_approval = "blocked"
    db.session.commit()
    flash(f"{professional.full_name} has been blocked.", "success")
    return redirect(url_for('admin_professional_details', professional_id=professional_id, user_id=user_id))

@app.route('/unblock_professional/<professional_id>/<user_id>', methods=['POST'])
def unblock_professional(professional_id, user_id):
    professional = ServiceProvider.query.filter_by(id=professional_id).first()
    if not professional:
        flash("Professional not found.", "danger")
        return redirect(url_for('admin_dashboard', user_id=user_id))
    professional.admin_approval = "approved"
    db.session.commit()    
    flash(f"{professional.full_name} has been unblocked and approved.", "success")
    return redirect(url_for('admin_professional_details', professional_id=professional_id, user_id=user_id))

@app.route('/admin_customer_details/<customer_id>/<user_id>')
def admin_customer_details(customer_id, user_id):
    customer = Customer.query.filter_by(id=customer_id).first()
    if not customer:
        flash("Customer not found.", "danger")
        return redirect(url_for('admin_dashboard', user_id=user_id))
    return render_template('customer_details.html', customer=customer, user_id=user_id)

@app.route('/block_customer/<customer_id>/<user_id>', methods=['POST'])
def block_customer(customer_id, user_id):
    customer = Customer.query.filter_by(id=customer_id).first()
    if not customer:
        flash("Customer not found.", "danger")
        return redirect(url_for('admin_dashboard', user_id=user_id))
    customer.admin_status = "blocked"
    db.session.commit()
    flash(f"{customer.full_name} has been blocked.", "success")
    return redirect(url_for('admin_customer_details', customer_id=customer_id, user_id=user_id))

@app.route('/unblock_customer/<customer_id>/<user_id>', methods=['POST'])
def unblock_customer(customer_id, user_id):
    customer = Customer.query.filter_by(id=customer_id).first()
    if not customer:
        flash("Customer not found.", "danger")
        return redirect(url_for('admin_dashboard', user_id=user_id))
    customer.admin_status = "approved"
    db.session.commit()
    flash(f"{customer.full_name} has been unblocked and approved.", "success")
    return redirect(url_for('admin_customer_details', customer_id=customer_id, user_id=user_id))

@app.route('/service-request/<request_id>/<user_id>', methods=['GET'])
def service_request_details(request_id, user_id):
    service_request = ServiceRequests.query.get(request_id)
    if not service_request:
        flash('Service request not found.', 'danger')
        return redirect(url_for('admin_dashboard', user_id=user_id))
    return render_template('service_request_details.html', service_request=service_request, user_id=user_id)

@app.route("/customer_dashboard/<user_id>")
def customer_dashboard(user_id):
    services = Service.query.all()
    service_requests = ServiceRequests.query.filter_by(customer_email=user_id).all()
    service_providers_for_history = []
    for request in service_requests:
        provider = ServiceProvider.query.filter_by(user_id=request.provider_email).first()
        if provider:
            service_providers_for_history.append({
                'provider': provider,
                'request': request
            })
    return render_template(
        "customer_dashboard.html", 
        user_id=user_id, 
        services=services,
        service_requests=service_requests,
        service_providers_for_history=service_providers_for_history
    )

@app.route("/customer_dashboard2/<user_id>/<service_name>", methods=["GET"])
def customer_dashboard2(user_id, service_name):
    service_requests = ServiceRequests.query.filter_by(customer_email=user_id).all()
    service_providers_for_history = []
    for request in service_requests:
        provider = ServiceProvider.query.filter_by(user_id=request.provider_email).first()
        if provider:
            service_providers_for_history.append({
                'provider': provider,
                'request': request 
            })
    service = ServiceProvider.query.filter(
        ServiceProvider.admin_approval == 'approved',
        ServiceProvider.service_name == service_name
    ).all()
    service_providers_for_booking = []
    for provider in service:
        provider_requests = ServiceRequests.query.filter_by(provider_email=provider.user_id).all()
        if not provider_requests or any(r.service2_status in ['requested', 'closed', 'rejected','cancelled'] for r in provider_requests):
            service_providers_for_booking.append({
                'provider': provider,
                'request': provider_requests[-1] if provider_requests else None  
            })
    return render_template(
        'customer_dashboard2.html', 
        user_id=user_id, service_name=service_name, service_providers_for_history=service_providers_for_history, service=service, service_providers_for_booking=service_providers_for_booking
    )

@app.route("/customer_search/<user_id>", methods=["GET", "POST"])
def customer_search(user_id):
    service_providers_for_booking = []
    search_term = request.form.get("search_term", "").strip()
    if request.method == "POST" and search_term:
        service = ServiceProvider.query.filter(
            ServiceProvider.admin_approval == 'approved'
        ).all()
        for provider in service:
            provider_requests = ServiceRequests.query.filter_by(provider_email=provider.user_id).all()
            if not provider_requests or any(r.service2_status in ['requested', 'closed', 'rejected'] for r in provider_requests):
                matches_search = (
                    (not search_term or provider.full_name.lower().find(search_term.lower()) != -1)
                    or (not search_term or provider.service_name.lower().find(search_term.lower()) != -1)
                    or (not search_term or provider.pincode.find(search_term) != -1)  
                )
                if matches_search:
                    service_providers_for_booking.append({
                        'provider': provider,
                        'request': provider_requests[-1] if provider_requests else None  
                    })
    return render_template("customer_search.html", user_id=user_id, service_providers_for_booking=service_providers_for_booking, search_term=search_term)

@app.route("/service_remarks/<provider_id>", methods=['GET', 'POST'])
def service_remarks(provider_id):
    provider = ServiceProvider.query.get(provider_id)
    user_id = request.args.get('user_id')    
    if not provider:
        return "Provider not found", 
    service_request = ServiceRequests.query.filter_by(
        provider_email=provider.user_id,
        customer_email=user_id,
        service2_status='In Progress'
    ).first()    
    if not service_request:
        return "Service request not found or not accepted",
    service_id = service_request.id
    if request.method == 'POST':
        rating = request.form.get('rating')
        remarks = request.form.get('remarks')
        request_time = request.form.get('request_time')
        if rating:
            new_rating = int(rating)
            if provider.rating == 0:
                provider.rating = new_rating
            else:
                provider.rating = (provider.rating + new_rating) / 2
        provider.remarks = remarks
        service_request = ServiceRequests.query.filter_by(
            provider_email=provider.user_id, 
            customer_email=user_id, 
            service_request_time=request_time, 
            service2_status='In Progress').first()
        if service_request:
            service_request.service2_status = 'closed'
            service_request.service_close_time = datetime.utcnow()
            service_request.remarks = remarks
            service_request.rating = rating
        db.session.commit()
        return redirect(url_for('customer_dashboard', user_id=user_id))
    return render_template("service_remarks.html", provider=provider, user_id=user_id,service_id=service_id)

@app.route("/book_service", methods=['POST'])
def book_service():
    provider_id = request.form.get('provider_id')  
    provider = ServiceProvider.query.get(provider_id)  
    user_id = request.form.get('user_id')
    customer = Customer.query.filter_by(user_id=user_id).first()
    if not provider:
        flash("Service provider not found.", "danger")
        return redirect(url_for('customer_dashboard2', user_id=user_id, service_name=""))
    existing_request = ServiceRequests.query.filter_by(
    customer_email=customer.user_id,
    provider_email=provider.user_id).filter(
    ServiceRequests.service2_status.in_(['requested', 'In Progress'])).first()
    if existing_request:
        if existing_request.service2_status == 'requested':
            flash("Service already requested for this provider.", "danger")
        elif existing_request.service2_status == 'In Progress':
            flash("Service already in Progress.", "danger")
        return redirect(url_for('customer_dashboard2', user_id=user_id, service_name=provider.service_name))
    customer_initials = "".join([name[0].upper() for name in customer.full_name.split()])
    service_initial = provider.service_name[0].upper()
    provider_initials = "".join([name[0].upper() for name in provider.full_name.split()])
    timestamp = datetime.utcnow().strftime("%d%m")
    timestamp2 = datetime.utcnow().strftime("%H%M%S")
    service_request_id = f"{customer_initials}{timestamp}{service_initial}{timestamp2}{provider_initials}"
    new_request = ServiceRequests(
        id=service_request_id,  
        customer_email=customer.user_id,
        provider_email=provider.user_id,
        serv_name=provider.service_name,
        service_request_time=datetime.utcnow(),
        service2_status='requested')
    db.session.add(new_request)
    provider.request_time = datetime.utcnow()
    db.session.commit()
    flash("Service successfully requested!", "success")
    return redirect(url_for('customer_dashboard2', user_id=user_id, service_name=provider.service_name))

@app.route("/provider_details/<provider_id>/<user_id>")
def provider_details(provider_id,user_id):
    provider = ServiceProvider.query.get(provider_id)
    if provider is None:
        flash("Provider not found.", "danger")
        return redirect(url_for('customer_search', user_id=user_id))
    return render_template('prof_det.html', provider=provider,user_id=user_id)

@app.route("/customer/service-request-details/<request_id>/<user_id>", methods=["GET", "POST"])
def customer_service_request_details(request_id, user_id):
    service_request = ServiceRequests.query.get(request_id)
    if not service_request:
        flash('Service request not found.', 'danger')
        return redirect(url_for('customer_dashboard', user_id=user_id))
    if request.method == "POST":
        service_request.service2_status = request.form.get("service2_status")
        service_request.remarks = request.form.get("remarks")
        service_request.rating = request.form.get("rating")
        db.session.commit()  
        flash("Service request updated successfully!", "success")
        return redirect(url_for('customer_service_request_details', request_id=request_id, user_id=user_id))
    return render_template("customer_service_request_edit.html", service_request=service_request, user_id=user_id)

@app.route("/cancel-service-request/<request_id>/<user_id>", methods=["GET", "POST"])
def cancel_service_request(request_id, user_id):
    service_request = ServiceRequests.query.get(request_id)
    if not service_request:
        flash("Service request not found.", "danger")
        return redirect(url_for('customer_dashboard', user_id=user_id)) 
    if request.method == "POST":
        if service_request.service2_status == 'requested':
            service_request.service2_status = 'cancelled'
            db.session.commit()
            flash("Service request has been cancelled.", "success")
        else:
            flash("You cannot cancel a service that is already in progress or closed.", "danger")
        return redirect(url_for('customer_dashboard', user_id=user_id))
    return redirect(url_for('customer_dashboard', user_id=user_id))

@app.route("/professional_dashboard/<user_id>")
def professional_dashboard(user_id):
    professional = ServiceProvider.query.filter_by(user_id=user_id).first()
    service_requests = ServiceRequests.query.filter_by(provider_email=user_id).all()
    requests_with_customers = []
    for request in service_requests:
        customer = Customer.query.filter_by(user_id=request.customer_email).first()
        if customer:
            requests_with_customers.append({
                "request": request,
                "customer_name": customer.full_name,
                "customer_address": customer.address,
                "customer_phone": customer.phone_number  
            })
    return render_template("professional_dashboard.html", user_id=user_id, professional=professional, requests_with_customers=requests_with_customers)

@app.route("/update_request_status", methods=["POST"])
def update_request_status():
    request_id = request.form.get("request_id")
    action = request.form.get("action")
    user_id = request.form.get("user_id")
    service_request = ServiceRequests.query.get(request_id)
    professional = ServiceProvider.query.filter_by(user_id=user_id).first()
    if service_request and professional:
        ongoing_request = ServiceRequests.query.filter_by(provider_email=professional.user_id, service2_status='In Progress').first()
        if action == "accept":
            if ongoing_request:
                flash("Complete the ongoing service to accept the new one.", "warning")
                return redirect(url_for("professional_dashboard", user_id=user_id))
            service_request.service2_status = "In Progress"
            professional.request_time=service_request.service_request_time        
        elif action == "reject":
            service_request.service2_status = "rejected"        
        db.session.commit()
    return redirect(url_for("professional_dashboard", user_id=user_id))

@app.route("/professional_search/<user_id>", methods=["GET", "POST"])
def professional_search(user_id):
    professional = ServiceProvider.query.filter_by(user_id=user_id).first()
    search_results = []
    search_term = request.form.get("search_term", "").strip()
    if request.method == "POST" and search_term:
        service_requests = (
            db.session.query(ServiceRequests, Customer)
            .join(Customer, ServiceRequests.customer_email == Customer.user_id)
            .filter(ServiceRequests.provider_email == user_id)
            .all())
        for sr, customer in service_requests:
            matches_customer_name = not search_term or search_term.lower() in customer.full_name.lower()
            matches_pincode = not search_term or search_term in customer.pincode
            matches_date = not search_term or search_term in str(sr.service_request_time.date())
            if matches_customer_name or matches_pincode or matches_date:
                search_results.append({
                    "request": sr,
                    "customer_name": customer.full_name,
                    "customer_address": customer.address,
                    "customer_phone": customer.user_id,
                    "date": sr.service_request_time
                })
    return render_template("professional_search.html",user_id=user_id,professional=professional,search_results=search_results,search_term=search_term)

@app.route("/edit_profile/<user_id>", methods=['GET', 'POST'])
def edit_profile(user_id):
    professional = ServiceProvider.query.filter_by(user_id=user_id).first()
    if not professional:
        return "Professional not found",
    if request.method == 'POST':
        full_name = request.form['full_name']
        phone_number = request.form['phone_number']
        service_name = request.form['service_name']
        experience_years = request.form['experience_years']
        pincode = request.form['pincode']
        service_description = request.form['service_description']
        professional.full_name = full_name
        professional.phone_number = phone_number
        professional.service_name = service_name
        professional.experience_years = experience_years
        professional.pincode = pincode
        professional.job_description = service_description
        db.session.commit()
        return redirect(url_for('professional_dashboard', user_id=user_id))
    return render_template("edit_profile.html", professional=professional, services=Service.query.all())

@app.route("/professional_customer_details/<customer_id>/<user_id>")
def professional_customer_details(customer_id, user_id):
    customer = Customer.query.filter_by(user_id=customer_id).first()
    if not customer:
        flash("Customer not found.", "danger")
        return redirect(url_for('professional_dashboard', user_id=user_id))
    service_requests = ServiceRequests.query.filter_by(customer_email=customer_id).all()
    rating = sum(req.rating for req in service_requests if req.rating) / len(service_requests) if service_requests else "No Ratings Yet"
    return render_template("cust_det.html",customer=customer,user_id=user_id,rating=rating)

@app.route("/prof_cus_serv_req/<customer_email>/<user_id>")
def prof_cus_serv_req(customer_email, user_id):
    customer = Customer.query.filter_by(user_id=customer_email).first()
    if not customer:
        flash("Customer not found.", "danger")
        return redirect(url_for('professional_dashboard', user_id=user_id))
    service_requests = ServiceRequests.query.filter_by(customer_email=customer_email).all()
    rating = sum(req.rating for req in service_requests if req.rating) / len(service_requests) if service_requests else "No Ratings Yet"
    return render_template("prof_cus_serv_req.html", customer=customer, service_requests=service_requests, rating=rating, user_id=user_id)

@app.route('/rate_customer', methods=['POST'])
def rate_customer():
    request_id = request.form.get('request_id')
    customer_email = request.form.get('customer_email')
    user_id = request.form.get('user_id')
    rating = request.form.get('rating')
    if request_id and customer_email and rating:
        service_request = ServiceRequests.query.get(request_id)
        customer = Customer.query.filter_by(user_id=customer_email).first()
        if service_request and customer:
            new_rating = int(rating)
            if customer.rating2 is None or customer.rating2 == 0:
                customer.rating2 = new_rating
            else:
                customer.rating2 = (customer.rating2 + new_rating) / 2
            db.session.commit()
            flash('Rating submitted successfully!', 'success')
        else:
            flash('Invalid request or customer.', 'danger')
    return redirect(url_for('professional_dashboard',user_id=user_id))
@app.route('/prof_serv_req/<service_request_id>/<user_id>')
def prof_serv_req(service_request_id, user_id):
    service_request = ServiceRequests.query.get(service_request_id)
    return render_template('prof_serv_req.html', service_request=service_request, user_id=user_id)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))
