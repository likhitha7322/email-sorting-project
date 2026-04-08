# 📧 Email Sorting OpenEnv Project

## 🚀 Overview

This project implements an **Email Sorting Environment** where different AI agents classify emails into categories such as **Spam, Important, Promotions, and Updates**.

It evaluates agent performance using metrics like:

* Accuracy
* Macro F1 Score
* Weighted F1 Score
* Noise Robustness

---

## 🧠 Features

* Multiple agent implementations
* Noise testing for robustness
* Detailed evaluation metrics
* Confusion matrix analysis
* HTML report generation

---

## 📂 Project Structure

```
├── Evaluate.py        # Main evaluation script
├── baseline.py        # Baseline agent
├── agents.py          # All agent implementations
├── env.py             # Email environment
├── models.py          # Data models & metrics
├── tasks.py           # Dataset / tasks
├── Report.py          # Generates HTML report
├── Report.html        # Output report
├── requirements.txt   # Dependencies
└── README.md
```

---

## ⚙️ Installation

Install dependencies:

```
pip install -r requirements.txt
```

---

## ▶️ How to Run

### Run full evaluation:

```
python Evaluate.py
```

### Run baseline:

```
python baseline.py
```

### Generate report:

```
python Report.py
```

---

## 📊 Output

* Console leaderboard of agents
* Accuracy by difficulty levels
* HTML report (`Report.html`)

---

## 🌐 Example Results

* EASY → High accuracy
* MEDIUM → Moderate accuracy
* HARD → Challenging classification

---

## 🛠️ Technologies Used

* Python
* Machine Learning concepts
* Evaluation metrics (F1, Accuracy)

---

## 📌 Notes

* Do not upload `__pycache__` or `.pyc` files
* Ensure all dependencies are installed before running

---

## 👩‍💻 Author

**Likhitha Halappa**

---

## ⭐ Acknowledgment

This project is developed as part of an AI evaluation environment for email classification tasks.
