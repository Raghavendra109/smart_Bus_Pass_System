# CodeAlpha – Cloud-Based Bus Pass Management System

## Project Overview
SmartPass is a cloud-hosted bus pass management system developed using Python Flask and deployed on AWS EC2. It allows users to apply for bus passes online, make simulated payments, and access digital bus passes with QR code verification.

## Features

- User registration and login
- Online bus pass applications
- Admin dashboard
- Admin approval and rejection
- Simulated online payment
- Digital bus pass generation
- QR code verification
- User application dashboard
- Responsive website design

## Technologies Used

- Python
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript
- AWS EC2
- Ubuntu Linux
- Gunicorn
- Git and GitHub

## Cloud Deployment

The application is deployed on an AWS EC2 Ubuntu instance and served using Gunicorn.

## Live Website

http://13.55.92.6

## GitHub Repository

https://github.com/Raghavendra109/CodeAlpha_CloudBasedBusPassSystem

## Project Structure

```text
CodeAlpha_CloudBasedBusPassSystem/
│
├── app.py
├── init_db.py
├── requirements.txt
├── static/
│   └── style.css
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── admin.html
│   ├── my_passes.html
│   └── digital_pass.html
│
└── README.md
```

## Installation

1. Clone the repository.
2. Install Python dependencies using `pip install -r requirements.txt`.
3. Initialize the database if required.
4. Configure the application secret and admin credentials securely.
5. Run the Flask application.

## Payment Information

The payment functionality is simulated for demonstration purposes. No real financial transactions are processed.

## Internship

Developed as part of the CodeAlpha Cloud Computing Internship – Task 3.
