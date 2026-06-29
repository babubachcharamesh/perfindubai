# 💰 Personal Finance Manager

A comprehensive, interactive web application built with **Streamlit**, **Pandas**, and **Plotly** to track expenses, manage multi-account balances, monitor budgets, automate recurring transactions, set financial goals, and visualize analytics in real time.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Repository Structure](#-repository-structure)
- [Data Storage Architecture](#-data-storage-architecture)
- [Local Installation & Setup](#-local-installation--setup)
  - [Option A: Using `uv` (Recommended)](#option-a-using-uv-recommended)
  - [Option B: Using Standard `pip` & Virtual Environment](#option-b-using-standard-pip--virtual-environment)
- [Streamlit Cloud Deployment Guide](#-streamlit-cloud-deployment-guide)
- [Configuration & Settings](#-configuration--settings)
- [License](#-license)

---

## 🌐 Overview

The **Personal Finance Manager** provides individuals and freelancers with an intuitive dashboard to master their personal cash flow. Built completely in Python using Streamlit, this light-weight solution requires zero complex database setups, persisting data cleanly in local JSON stores while offering rich visualization and analytical reporting tools.

---

## ✨ Key Features

### 📊 Financial Dashboard
- **Real-Time KPIs**: Track total net worth across accounts, monthly income, monthly expenses, and net monthly savings.
- **Cash Flow Summary**: Quick overview of top spending categories and recent financial movements.

### 💰 Transaction Management
- **Full Transaction Lifecycle**: Add, edit, filter, search, and delete transactions.
- **Transaction Types**: Support for `Income`, `Expense`, and `Account Transfers`.
- **Metadata Support**: Categorize transactions, append notes, assign custom tags, and associate them with specific financial accounts.
- **Export Capabilities**: Download transaction records to CSV for offline analysis.

### 🏦 Multi-Account Tracking
- **Account Types**: Manage Cash, Checking/Savings Bank Accounts, Credit Cards, and Investment portfolios.
- **Automated Balance Calculation**: Account balances automatically calculate and reconcile based on income, expenses, and inter-account transfers.
- **Custom Account Profiles**: Assign unique icons, colors, and initial balances.

### 📋 Budgeting & Expense Control
- **Category Budgets**: Define custom spending caps for categories like Food, Housing, Utilities, and Entertainment.
- **Visual Progress Bars**: Real-time visual meters showing percentage consumed.
- **Alert Indicators**: Color-coded warning notifications when budget thresholds are exceeded.

### 🎯 Financial Goals
- **Savings Goals**: Set target savings for milestones (e.g., Emergency Fund, New Car, Vacation).
- **Target Deadlines**: Track required daily/monthly savings contributions based on target completion dates.

### 🔄 Recurring Transactions Automation
- **Automated Logging**: Schedule recurring salary deposits, subscription fees, or utility bills.
- **Flexible Frequencies**: Support for Daily, Weekly, Monthly, and Yearly intervals.

### 📈 Reports & Deep Analytics
- **Interactive Plotly Visualizations**: Sunburst charts, category expense pie charts, and monthly comparison bar charts.
- **Trend Analysis**: Analyze multi-month income vs. expense cash flows and cumulative net worth progression.

### ⚙️ Customization & Control
- **Multi-Currency**: Seamlessly switch display symbols between USD ($), EUR (€), GBP (£), JPY (¥), INR (₹), CAD (C$), and AUD (A$).
- **Custom Categories**: Add or remove custom income and expense categories.
- **Data Governance**: Reset or clear transaction histories directly from the app interface.

---

## 🛠️ Tech Stack

- **Core Framework**: [Streamlit](https://streamlit.io/) (v1.30.0+)
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/) (v2.0.0+)
- **Data Visualization**: [Plotly Express & Graph Objects](https://plotly.com/python/) (v5.18.0+)
- **Package Management**: [uv](https://github.com/astral-sh/uv) / `pip`
- **Persistence Layer**: Structured JSON Storage (`finance_data/`)

---

## 📁 Repository Structure

```text
.
├── finance_data/              # Local data storage directory
│   ├── accounts.json          # User financial accounts data
│   ├── budgets.json           # Active monthly budgets
│   ├── categories.json        # Income and expense category schemas
│   ├── goals.json             # Financial savings goals
│   ├── recurring.json        # Scheduled recurring transactions
│   ├── settings.json         # App preferences & currency configurations
│   └── transactions.json      # Main financial transaction records
├── .gitignore                 # Files and folders ignored by Git
├── main.py                    # Main Streamlit application entry point
├── pyproject.toml             # Project metadata and dependencies (uv / pip)
├── README.md                  # Comprehensive project documentation
└── requirements.txt           # Standard Python requirements for deployment
```

---

## 💾 Data Storage Architecture

All user state and data records are stored in human-readable JSON files inside the `finance_data/` folder. The application automatically initializes default schemas if files are missing.

| File | Description |
| :--- | :--- |
| `transactions.json` | Stores individual income, expense, and transfer records with timestamps, amounts, and account IDs. |
| `accounts.json` | Contains account profiles, types (Bank, Cash, Credit), and assigned colors/icons. |
| `budgets.json` | Maps monthly monetary limits to specific expense categories. |
| `goals.json` | Tracks targeted target amounts, current saved balances, and deadline dates. |
| `recurring.json` | Keeps schedules for auto-generated recurring items along with execution timestamps. |
| `settings.json` | Stores global user configurations such as active currency and date formatting. |

---

## 🚀 Local Installation & Setup

Ensure you have Python 3.10 or higher installed on your system.

### Option A: Using `uv` (Recommended)

`uv` is an extremely fast Python package installer and resolver.

1. **Clone the repository**:
   ```bash
   git clone <your-repository-url>
   cd <repository-directory>
   ```

2. **Run the application directly with `uv`**:
   ```bash
   uv run streamlit run main.py
   ```
   *Note: `uv` will automatically manage the virtual environment and install dependencies listed in `pyproject.toml`.*

---

### Option B: Using Standard `pip` & Virtual Environment

1. **Clone the repository**:
   ```bash
   git clone <your-repository-url>
   cd <repository-directory>
   ```

2. **Create and activate a virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Streamlit app**:
   ```bash
   streamlit run main.py
   ```

5. **Access the web application**:
   Open your browser and navigate to `http://localhost:8501`.

---

## ☁️ Streamlit Cloud Deployment Guide

Deploying this application to **Streamlit Community Cloud** is free and takes only a few minutes.

### Step 1: Push Code to GitHub
Ensure all your project files (including `main.py`, `requirements.txt`, `pyproject.toml`, `.gitignore`, and `README.md`) are committed and pushed to a public or private GitHub repository:
```bash
git add .
git commit -m "Prepare Personal Finance Manager for Streamlit Cloud deployment"
git push origin main
```

### Step 2: Deploy on Streamlit Community Cloud
1. Visit [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.
2. Click on the **"New app"** button.
3. Select your repository, branch (e.g., `main` or `master`), and specify the main file path:
   - **Main file path**: `main.py`
4. Click **"Deploy!"**.

Streamlit Cloud will automatically detect `requirements.txt`, install dependencies, and launch your Personal Finance Manager web application.

---

## ⚙️ Configuration & Settings

You can customize the application behavior directly from the user interface under the **⚙️ Settings** tab:
- **Currency**: Switch between `$`, `€`, `£`, `¥`, `₹`, `C$`, and `A$`.
- **Date Format**: Choose your preferred display layout (`YYYY-MM-DD`, `DD-MM-YYYY`, or `MM/DD/YYYY`).
- **Category Customization**: Add new categories tailored to your personal financial workflow or remove unused defaults.

---

## 📄 License

This project is open-source and available under the MIT License. Feel free to customize and expand it for your personal or commercial financial needs!
