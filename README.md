# Placement-Hub

STEPS TO RUN PLACEMIND.AI

1. Clone the repository
git clone <your-repo-url>
cd placemind.ai


BACKEND (FastAPI)

2. Create virtual environment
python -m venv venv

3. Activate virtual environment
Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

4. Install backend dependencies
pip install -r requirements.txt

5. Create .env file in backend folder
DATABASE_URL=your_database_url
JWT_SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

6. Run backend server
uvicorn app.main:app --reload

Backend runs on:
http://127.0.0.1:8000
Swagger docs:
http://127.0.0.1:8000/docs


FRONTEND (React + Vite)

7. Go to frontend folder
cd frontend

8. Install frontend dependencies
npm install

9. Start frontend
npm run dev

Frontend runs on:
http://localhost:5173


USING THE APPLICATION

10. Register user (student or coordinator)

11. Login user

12. If student, fill Student Profile and click Save Profile

Only one profile is created per user.
Existing profile is updated on save.
