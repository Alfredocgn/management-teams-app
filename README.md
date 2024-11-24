# Backend
## Management Teams API
This API allows for managing work teams. The backend is developed in Python using the FastAPI framework, with PostgreSQL as the database. The project includes a Docker container for the database and uses SQLAlchemy as the ORM to manage database tables. It is designed to handle work teams, users, projects, and tasks for each project. Additionally, the API manages user subscriptions via Stripe and handles user authentication using JWT.

# Instructions:

Step 1: Clone the repository
`git clone <repository-url>`

Step 2: Create a virtual environment with Python
`virtualenv venv`

Step 3: Navigate to the backend folder
`cd backend`

Step 4: Install dependencies
`pip install -r requirements.txt`

Step 5: Ensure Docker Desktop is installed

Step 6: Start the Docker container
`docker compose up -d`

Step 7: Navigate to the app folder
`cd app`

Step 8: Run the app
`uvicorn main:app --reload`

# Frontend
## Management Teams Frontend
This project is a React application that interacts with the Management Teams API. It is designed to manage work teams, users, projects, and tasks for each project. Additionally, it manages user subscriptions via Stripe and handles user authentication using JWT.

# Instructions: 
Step 1: Clone the repository
`git clone <repository-url>`

Step 2: Navigate to the frontend folder
`cd frontend`

Step 3: Install dependencies
`npm install` 

Step 4: Run the app
`npm run dev`