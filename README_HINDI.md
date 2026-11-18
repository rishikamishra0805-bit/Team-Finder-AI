# TEAM FINDER AI — Starter Prototype

**Tagline:** Build Better Teams. Turn Ideas Into Reality.

Yeh ek working college-project MVP/starter hai. Isme Flask + SQLite use hua hai.

## 1. Is ZIP mein kya ready hai?

- Registration aur login
- Password hashing (password plain text mein save nahi hota)
- User talent profile: skills, interests, role, experience, availability, goals
- Project create/publish karna
- Saare published projects explore karna
- Project ke liye candidate match suggestions
- Explainable matching score aur reasons
- Responsive basic UI
- SQLite database automatic create hota hai

## 2. Matching kaise hoti hai?

Abhi matching engine **rule-based weighted scoring** use karta hai. Yeh trained AI/ML model nahi hai. Score ke 8 dimensions hain:
1. Skill compatibility — 30%
2. Role compatibility — 15%
3. Interest alignment — 10%
4. Experience level — 10%
5. Availability — 10%
6. Goal alignment — 10%
7. Work preference — 5%
8. Contribution / requested skill coverage — 10%

Formula: `Match Score = sum(weight × criterion score) × 100`

Yeh weights prototype ke starting values hain; team/user feedback aur testing ke baad adjust karne chahiye. Scores ko final truth nahi, recommendation estimate samjhein.

## 3. Windows laptop par setup

### Requirements
- Python 3.11 recommended
- VS Code (optional, code edit karne ke liye)
- Internet only for first-time package installation; Google Fonts optional

### Steps
1. ZIP extract karein. Folder ka naam `Team_Finder_AI` rehne dein.
2. Folder ke andar terminal open karein (VS Code: Terminal → New Terminal).
3. Virtual environment banayein:

```powershell
py -3.11 -m venv venv
```

4. Activate karein:

```powershell
.\venv\Scripts\activate
```

5. Packages install karein:

```powershell
python -m pip install -r requirements.txt
```

6. App run karein:

```powershell
python run.py
```

7. Browser mein yeh address kholein:

`http://127.0.0.1:5000`

8. Register karein, profile fill karein, phir project create karein. Doosre test candidate ke liye alag email se second account banayein.

### Agar `py -3.11` command kaam na kare
Python 3.11 installed hai ya nahi check karein:

```powershell
py --list
```

Agar Python 3.11 nahi hai, Python 3.11 install karke setup repeat karein. Python 3.14 ke saath kuch libraries ki compatibility alag ho sakti hai; isliye 3.11 recommended hai.

## 4. Folder structure

```text
Team_Finder_AI/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── matching.py
│   ├── templates/
│   └── static/
├── config.py
├── run.py
├── requirements.txt
├── README_HINDI.md
└── .gitignore
```

## 5. Abhi kya nahi bana hai / humein aage kya add karna hai?

- Real trained ML/NLP model; current score explainable rule-based algorithm hai
- Team combination optimizer (sirf individual candidate ranking hai)
- Invitation accept/reject workflow
- In-app chat, notifications, task assignment, team progress dashboard
- Email/OTP verification, password reset
- Admin panel and moderation/reporting
- Production security hardening, deployment, backups
- Proper privacy policy, terms and consent
- Market validation, user testing, feedback and evaluation report

## 6. Important demo plan

1. Account A register karein, profile mein skills add karein.
2. Account A se ek project create karein, required skills/roles likhein.
3. Logout karke Account B register karein.
4. Account B ka profile complete karein.
5. Dashboard par recommended projects aur score dekhein.
6. Project detail par candidate matching section dekhein.

**Note:** Demo mein real students ka personal data bina permission use na karein. Dummy/test accounts use karein.

## 7. Project ko college presentation mein kaise describe karein?

"Team Finder AI is an AI-assisted team formation platform. It collects project requirements and member profiles, then calculates explainable compatibility scores across skills, roles, interests, experience, availability, goals and work preferences. The current prototype implements a transparent weighted rule-based matching engine. A trained recommendation model and collaboration features are planned future enhancements."

Features ko presentation mein implemented tabhi batayein jab aapne unhe run karke test kar liya ho.
