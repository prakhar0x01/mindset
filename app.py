from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import hashlib
import json


app = Flask(__name__)
app.config['SECRET_KEY'] = 'cHJha2hhcjB4MDE6YWRtaW4='
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_male = db.Column(db.Boolean, nullable=False)
    financial_problems = db.Column(db.Boolean, nullable=False)
    procrastination = db.Column(db.Boolean, nullable=False)
    addiction = db.Column(db.Boolean, nullable=False)
    heartbreak = db.Column(db.Boolean, nullable=False)
    stress = db.Column(db.Boolean, nullable=False)
    move_out = db.Column(db.Boolean, nullable=False)
    def check_password(self, password):
        password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return password == self.password


with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Default Page is Login
@app.route('/',methods=['GET','POST'])
def default():
    if request.method == 'POST' or request.method == 'GET':
        return redirect(url_for('login'))


# Content Upload
@app.route('/admin/content', methods=['GET','POST'])
@login_required
def content():

    if request.method == 'GET': 
        if current_user.username != 'admin':
            return redirect(url_for('login'))    

    if request.method == 'POST':
        link = request.form['link']
        option = request.form['option']
        content_type = request.form['content_type']

        # Save the video link and option to the text file
        if content_type == 'reel':
            with open('reel_links.txt', 'a') as file:
                file.write(f"{option} : https://youtube.com/embed/{link}&amp;controls=0\n")

            message = 'Reel Added successfully!'
            return render_template('content.html',success=message)

        if content_type == 'video':
            with open('video_links.txt', 'a') as file:
                file.write(f"{option} : https://youtube.com/embed/{link}&amp;controls=0\n")

            message = 'Video Added successfully!'
            return render_template('content.html',success=message)

        else:
            message = 'Please choose all options.'
            return render_template('content.html',error=message)

    return render_template('content.html')


# Publish Writing
@app.route('/admin/publish', methods=['POST','GET'])
@login_required
def writing():

    if request.method == 'GET': 
        if current_user.username != 'admin':
            return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        with open('blogs.txt', 'a') as file:
            file.write(f"{title}\n{content}\n\n")

        message = 'Blog post published successfully.'
        return render_template('write.html',success=message)

    return render_template('write.html')    


# Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_male = bool(request.form['gender'] == 'male')
        financial_problems = bool(request.form['financial_problems'] == 'yes')
        procrastination = bool(request.form['procrastination'] == 'yes')
        addiction = bool(request.form['addiction'] == 'yes')
        heartbreak = bool(request.form['heartbreak'] == 'yes')
        stress = bool(request.form['stress'] == 'yes')
        move_out = bool(request.form['move_out'] == 'yes')

        if not username or not password or not email:
            flash('Please enter all fields')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            message = "User with that Email already exists."
            return render_template("signup.html",error=message)

        if User.query.filter_by(username=username).first():
            message = "User with that username already exists."
            return render_template("signup.html",error=message)

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        user = User(username=username, email=email ,password=hashed_password,is_male=is_male,financial_problems=financial_problems,procrastination=procrastination,addiction=addiction,heartbreak=heartbreak,stress=stress,move_out=move_out)
        db.session.add(user)
        db.session.commit()

        flash('Successfully registered!')
        return redirect(url_for('success'))

    return render_template('signup.html')

# Success Page
@app.route('/success',methods=['GET'])
def success():
    return render_template('success.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username and password:
            with app.app_context():
                user = User.query.filter_by(username=username).first()
                if user is not None and user.check_password(password):
                    login_user(user)
                    return redirect(url_for('protected'))

            message = "Invalid Credentials."
            return render_template('login.html',error=message)

    return render_template('login.html')

# Admin Portal
@app.route('/admin', methods=['GET'])
@login_required
def internal():
    if request.method == 'GET': 
        if current_user.username != 'admin':
            return redirect(url_for('login'))

    users = User.query.all()
    return render_template('users.html', users=users)


# Home page after login
@app.route('/protected')
@login_required
def protected():
    with app.app_context():
        user = current_user
        message = 'Hello, ' + user.username + '!'
        email = user.email
        return render_template('protected.html',username=message,email=email)


# Logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# Reels and Shorts
@app.route('/protected/shorts', methods=['GET'])
@login_required
def display_shorts():
    if request.method == 'GET':
        with open('reel_links.txt', 'r') as file:
            video_data = file.read()

        stress = current_user.stress
        addiction = current_user.addiction
        financial_problems = current_user.financial_problems
        procrastination = current_user.procrastination
        heartbreak = current_user.heartbreak
        move_out = current_user.move_out
        is_male = current_user.is_male
#        print(stress)
        option_videos = []


        while True:
            for line in video_data.splitlines():
                if line.startswith('stress :') and stress!=False:
                    reel_link = line.split(' ')[2].strip()
    #               print(reel_link)
                    option_videos.append(reel_link)

                if line.startswith('addiction :') and addiction!=False:
                        reel_link = line.split(' ')[2].strip()
                        print(reel_link)
                        option_videos.append(reel_link)

                if line.startswith('financial_problems :') and financial_problems!=False:
                        reel_link = line.split(' ')[2].strip()
                        print(reel_link)
                        option_videos.append(reel_link)

                if line.startswith('procrastination :') and procrastination!=False:
                        reel_link = line.split(' ')[2].strip()
                        print(reel_link)
                        option_videos.append(reel_link)

                if line.startswith('heartbreak :') and heartbreak!=False:
                        reel_link = line.split(' ')[2].strip()
                        print(reel_link)
                        option_videos.append(reel_link)

                if line.startswith('move_out :') and move_out!=False:
                        reel_link = line.split(' ')[2].strip()
                        print(reel_link)
                        option_videos.append(reel_link)

                if line.startswith('is_male :') and is_male!=False:
                        reel_link = line.split(' ')[2].strip()
                        print(reel_link)
                        option_videos.append(reel_link)

            return render_template('shorts.html', option_videos=option_videos)


# Long form videos 
@app.route('/protected/videos', methods=['GET'])
@login_required
def display_videos():
    if request.method == 'GET':
        with open('video_links.txt', 'r') as file:
            video_data = file.read()

        stress = current_user.stress
        addiction = current_user.addiction
        financial_problems = current_user.financial_problems
        procrastination = current_user.procrastination
        heartbreak = current_user.heartbreak
        move_out = current_user.move_out
        is_male = current_user.is_male
#        print(stress)
        option_videos = []


        while True:
            for line in video_data.splitlines():
                if line.startswith('stress :') and stress!=False:
                    video_link = line.split(' ')[2].strip()
    #               print(video_link)
                    option_videos.append(video_link)

                if line.startswith('addiction :') and addiction!=False:
                        video_link = line.split(' ')[2].strip()
                        print(video_link)
                        option_videos.append(video_link)

                if line.startswith('financial_problems :') and financial_problems!=False:
                        video_link = line.split(' ')[2].strip()
                        print(video_link)
                        option_videos.append(video_link)

                if line.startswith('procrastination :') and procrastination!=False:
                        video_link = line.split(' ')[2].strip()
                        print(video_link)
                        option_videos.append(video_link)

                if line.startswith('heartbreak :') and heartbreak!=False:
                        video_link = line.split(' ')[2].strip()
                        print(video_link)
                        option_videos.append(video_link)

                if line.startswith('move_out :') and move_out!=False:
                        video_link = line.split(' ')[2].strip()
                        print(video_link)
                        option_videos.append(video_link)

                if line.startswith('is_male :') and is_male!=False:
                        video_link = line.split(' ')[2].strip()
                        print(video_link)
                        option_videos.append(video_link)

            return render_template('videos.html', option_videos=option_videos)        

#                else:
#                    flash('You do not have any problems identified. Videos are not recommended for you.')
#                    return render_template('videos.html', option_videos=None)

@app.route('/protected/read', methods=['GET'])
@login_required
def read():
    if request.method == 'GET':
        with open('blogs.txt', 'r') as file:
            blog_data = file.read()

        blogs = []
        for blog_entry in blog_data.split('\n\n'):
            blog_entry = blog_entry.strip()
            if blog_entry:
                title, content = blog_entry.split('\n', 1)
                blogs.append({'title': title, 'content': content})

        return render_template('read.html', blogs=blogs)


tickets = []

# Creating Support Ticket for normal user
@app.route('/support', methods=['POST','GET'])
@login_required
def support():
    if request.method == 'POST':
        name = request.form['name']
        message = request.form['message']

        # Generate a unique ticket ID
        ticket_id = len(tickets) +2023+ current_user.id + 1

        # Create a new ticket entry
        new_ticket = {
            'ticket_id': ticket_id,
            'name': name,
            'username':current_user.username,
            'email': current_user.email,
            'message': message,
        }

        # Add the new ticket to the list of tickets
        tickets.append(new_ticket)

        # Save the updated ticket data to JSON file
        with open('tickets.json', 'w') as file:
            json.dump(tickets, file, indent=4)

#        with open('backup_tickets.json', 'w') as file:
#            json.dump(tickets, file, indent=4)  

        message = f'Hii {current_user.username}\n\nYour Support Ticket [Ticket-Id: {ticket_id}]  has been created successfully. we will get back to you soon.\nThanks\nMindset Support Team'
        return render_template('support.html',success=message)

    return render_template('support.html')

# Admin To see users Support Tickets
@app.route('/admin/tickets/', methods=['GET'])
@login_required
def view_ticket():
    if request.method == 'GET': 
        if current_user.username != 'admin':
            return redirect(url_for('login'))

    with open('tickets.json', 'r') as file:
        tickets = json.load(file)

    return render_template('tickets.html', tickets=tickets)

# About-Us Page
@app.route('/about_us', methods=['GET'])
def about_us():
    message = 'Hello, ' + current_user.username + '!'
    email = current_user.email
    return render_template('about_us.html',username=message,email=email)
    

if __name__ == '__main__':
    app.run(debug=True)
