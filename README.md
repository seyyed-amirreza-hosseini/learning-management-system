# Learning Management System (LMS)
## Overview

Welcome to the Learning Management System (LMS) built with Django! This application is designed to streamline the online education experience for students, teachers, and administrators. It serves as a comprehensive platform where users can manage courses, engage in discussions, track learning progress, and facilitate virtual meetings, all in one integrated environment.

## Features

- **User Management**
  - Custom user model with email as the unique identifier.
  - Role-based user management (Student, Teacher, Admin).
  - User registration, login, and logout functionalities.

- **Course Management**
  - Creation and management of courses with attributes like name, description, category, level, and price.
  - Assignment of multiple instructors to courses.
  - Reviews for courses with ratings and comments, including uniqueness constraints.

- **Module and Lesson Management**
  - Creation of modules associated with courses.
  - Lessons within modules, including various content types (video, article, quiz, etc.).

- **Enrollment System**
  - Enrollment of students in courses with tracking of enrollment date, progress, and status (active, completed, dropped).
  - Unique constraints on enrollments to prevent duplicate enrollments.

- **Assignments and Submissions**
  - Creation of assignments linked to lessons, including due dates and maximum scores.
  - Submission of assignments by students, with file upload capabilities and feedback.

- **Quizzes**
  - Creation of quizzes linked to lessons, including questions and choices.
  - Grading functionality for quizzes, tracking scores, and attempts.

- **Authentication With Google**
  - Users can sign up and log in using their Google accounts through OAuth integration.

- **Forums and Discussions**
  - Creation of forums associated with courses for discussions.
  - Posts and comments within forums, with user ownership permissions.

- **Activity Logging**
  - Logging of user activities (e.g., login, course views) for tracking purposes.

- **Analytics**
  - Endpoints for retrieving user activity logs and course completion rates.

- **Meetings Integration**
  - Scheduling meetings with a host, topic, start time, and meeting link.
  - Integration with Zoom API for creating online meetings.

- **CSV Report Generation**
  - Functionality to generate CSV reports of user course progress.

- **Permissions and Access Control**
  - Custom permissions to restrict access based on user roles (admin, teacher, student).
  - Object-level permissions for actions like creating, updating, and deleting resources.

- **Celery Tasks**
  - Background tasks for sending emails, such as assignment reminders and weekly reports.

## Backend Stack

This application is built using the following backend technologies:

- **Django**
- **Django REST Framework (DRF)**
- **PostgreSQL**
- **Celery**
- **Redis**
- **Zoom API**
  
## Installation

1. Clone the repository:
     ```
     git clone https://github.com/seyyed-amirreza-hosseini/learning-management-system.git
    ```

2. Navigate into the project directory:
      ```
      cd learning-management-system
      ```
3. Install dependencies (using Pipenv):
      ```
      pipenv install
      ```
4. Migrate the database:
    ```
    python manage.py migrate
    ```
5. Create a superuser:
    ```
    python manage.py createsuperuser
    ``` 

## Usage
Run the application with:
  ```
  python manage.py runserver
  ```

## Contributing

I welcome your contributions to help improve this project and make a positive impact on the learning community!
Please fork the repository and create a pull request with any improvements.

