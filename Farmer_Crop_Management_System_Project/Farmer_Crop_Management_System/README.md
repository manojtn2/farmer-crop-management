# Farmer Crop Management System

Student project for Manoj T N, M.Sc. IT, 2nd Year / 4th Semester.

## Features
- Farmer registration and login with hashed passwords
- Crop management (add, view, edit, delete)
- Farming activity records
- Expense records
- Harvest records and revenue calculation
- Dashboard and crop-wise profit/loss reports
- Responsive website UI

## Run on Windows
1. Install Python 3.10+.
2. Extract this ZIP and open the folder in VS Code.
3. In the terminal:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```
4. Visit http://127.0.0.1:5000
5. Register an account and start adding crop records.

SQLite is used by default so it works without configuring a database server. To use MySQL for the final demonstration, create the database `farmer_crop_db`, then set:
```powershell
$env:DATABASE_URL = "mysql+pymysql://root:YOUR_PASSWORD@localhost/farmer_crop_db"
python app.py
```
Replace `YOUR_PASSWORD` with your MySQL password. Tables are created automatically.

This is a local development starter project. Before public deployment, configure a strong secret key, disable debug mode, and add CSRF protection. The report's profit/loss is an estimate based on recorded expenses and harvest sales.
