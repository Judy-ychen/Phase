# Phase - Empowering Women Through Personalized Health Management


## Description: <br>
Phase is an innovative app designed to empower women to align their nutrition and fitness with the different phases of their menstrual cycle: Menstrual, Follicular, Ovulation,
and Luteal. By analyzing cycle length, Phase offers tailored food and exercise recommendations to support hormonal balance and promote a long-term healthy lifestyle.
Users can view their  personalized food and exercise recommendations at any current day. Our mission is to foster inclusivity by accounting for diverse cycle types and making 
healthy living accessible for all. With Phase, women take control of their health—one cycle at a time.

## Future Goal: <br>
Users receive personalized reminders via email, with seamless Google/Apple Calendar integration coming soon, ensuring effortless access. 

## Tech Stack

### Programming Language:
Python: Core programming language used for backend development.

### Frameworks and Libraries:
Flask: Lightweight web framework for building RESTful APIs. <br>
Flask-Bcrypt: For password hashing and user authentication.<br>
Flask-JWT-Extended: For implementing JSON Web Token (JWT)-based authentication.<br>
SQLAlchemy: ORM (Object Relational Mapper) used for database operations and models.<br>
Flask-SQLAlchemy: Extension that integrates SQLAlchemy with Flask.<br>

Datetime: Python’s standard library for date and time manipulations. <br>
Database: SQLite - Relational database for development and testing. Configured with SQLAlchemy.<br>

### Authentication and Security:
JWT (JSON Web Tokens): Secure user authentication and session handling. <br>
BCrypt: Hashing passwords for secure storage. <br>
Deployment Readiness: Environment configurations (e.g., JWT_SECRET_KEY, database URI) are easily adjustable for different environments (development/production).<br>


Our backend processes user input such as login information, name, age, weight, and period start and end dates, storing this data in an SQL database. 
The backend algorithm, built in Flask, determines the menstrual phase based on each individual's cycle length and provides tailored recommendations for nutrients, 
their sources, and types of exercise. The frontend, developed using Streamlit, offers an intuitive interface for users to interact with.

## Design <br>
<img width="1283" alt="截屏2024-11-17 上午11 19 12" src="https://github.com/user-attachments/assets/b309f9cb-1118-4826-bd5d-1703869d20f8">




## Features <br>
Phase offers a range of features designed to provide personalized and actionable health insights:
Personalized Nutrition and Fitness Recommendations: Tailored advice based on menstrual cycle phases. <br>
Cycle Data Management: Easy input and tracking of period start and end dates. <br>
Secure Authentication: Robust user authentication and data protection. <br>
Future Integration: Planned integration with Google and Apple Calendar for seamless reminders. <br>
Limitation: Streamlit runs  its own web server via the Tornado framework, and there’s no good way to embed a Streamlit app inside a Flask server. <br>
This might not be the right choice of platform for Frontend. <br>


## How to Run the Project: 
To set up and run Phase locally, follow these steps:

Open terminal from the folder Phase type follwed by python app.py. <br>
Open a new terminal window and type streamlit run streamlit_app.py.<br>
You will get the website to run and ready to input in the website.<br>
