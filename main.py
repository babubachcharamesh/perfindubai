import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date, timedelta
import calendar
from collections import defaultdict
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# ============================================================
# CONFIGURATION & DATA PERSISTENCE
# ============================================================
# NOTE: Data is stored per-user in browser localStorage via a custom HTML/JS component.
# No server-side files are written — each user's data is completely private.

import streamlit.components.v1 as components

# Declare browser local storage component
COMPONENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local_storage_component")
local_storage = components.declare_component("local_storage", path=COMPONENT_DIR)

# Default categories
DEFAULT_INCOME_CATEGORIES = ["Salary", "Freelance", "Investments", "Business", "Gifts", "Other Income"]
DEFAULT_EXPENSE_CATEGORIES = [
    "Housing", "Food & Dining", "Transportation", "Utilities",
    "Healthcare", "Entertainment", "Shopping", "Education",
    "Personal Care", "Travel", "Insurance", "Savings", "Debt Payment", "Other"
]

# ============================================================
# DATA MANAGEMENT FUNCTIONS
# ============================================================

def load_json(filepath, default=None):
    """No-op: data is stored in st.session_state, not on the server filesystem."""
    if default is None:
        default = []
    return default

def save_json(filepath, data):
    """No-op: data is stored in st.session_state, not on the server filesystem."""
    pass

def load_transactions():
    return []

def save_transactions(data):
    st.session_state.transactions = data
    st.session_state.trigger_save = True

def load_budgets():
    return []

def save_budgets(data):
    st.session_state.budgets = data
    st.session_state.trigger_save = True

def load_goals():
    return []

def save_goals(data):
    st.session_state.goals = data
    st.session_state.trigger_save = True

def load_accounts():
    return []

def save_accounts(data):
    st.session_state.accounts = data
    st.session_state.trigger_save = True

def load_categories():
    return {}

def save_categories(data):
    st.session_state.categories = data
    st.session_state.trigger_save = True

def load_recurring():
    return []

def save_recurring(data):
    st.session_state.recurring = data
    st.session_state.trigger_save = True

def load_settings():
    return {"currency": "USD", "theme": "light", "date_format": "%Y-%m-%d"}

def save_settings(data):
    st.session_state.settings = data
    st.session_state.trigger_save = True

def trigger_auto_save():
    """Trigger invisible local storage component to persist current session data to browser localStorage."""
    backup_data = {
        "transactions": st.session_state.transactions,
        "accounts":     st.session_state.accounts,
        "budgets":      st.session_state.budgets,
        "goals":        st.session_state.goals,
        "categories":   st.session_state.categories,
        "recurring":    st.session_state.recurring,
        "settings":     st.session_state.settings,
    }
    payload_str = json.dumps(backup_data, default=str)
    # Render component in save mode
    local_storage(action="save", payload=payload_str, key="auto_saver")
    st.toast("💾 Auto-saved data to browser localStorage!")

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

def init_session_state():
    """Initialise per-user session state with default values.
    Data never touches the server filesystem — it lives only in the user's
    browser session. Users download/upload a JSON file to persist across sessions.
    """
    if 'transactions' not in st.session_state:
        st.session_state.transactions = []
    if 'budgets' not in st.session_state:
        st.session_state.budgets = []
    if 'goals' not in st.session_state:
        st.session_state.goals = []
    if 'accounts' not in st.session_state:
        st.session_state.accounts = [
            {"id": 1, "name": "Cash", "type": "Cash", "balance": 0.0, "currency": "USD", "color": "#2ecc71", "icon": "💵"},
            {"id": 2, "name": "Bank Account", "type": "Bank", "balance": 0.0, "currency": "USD", "color": "#3498db", "icon": "🏦"},
            {"id": 3, "name": "Credit Card", "type": "Credit", "balance": 0.0, "currency": "USD", "color": "#e74c3c", "icon": "💳"},
        ]
    if 'categories' not in st.session_state:
        st.session_state.categories = {
            "income": DEFAULT_INCOME_CATEGORIES[:],
            "expense": DEFAULT_EXPENSE_CATEGORIES[:]
        }
    if 'recurring' not in st.session_state:
        st.session_state.recurring = []
    if 'settings' not in st.session_state:
        st.session_state.settings = {"currency": "USD", "theme": "light", "date_format": "%Y-%m-%d"}
    if 'trans_form_id' not in st.session_state:
        st.session_state.trans_form_id = 0
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def apply_theme_css():
    theme = st.session_state.settings.get("theme", "light")
    
    if theme == "dark":
        # Professional slate dark theme
        bg_color = "#0f172a"          # slate-900
        sec_bg_color = "#1e293b"      # slate-800
        text_color = "#f8fafc"        # slate-50
        label_color = "#94a3b8"       # slate-400
        primary_color = "#38bdf8"     # sky-400
        border_color = "#334155"      # slate-700
        progress_bg = "#475569"       # slate-600
        input_bg = "#1e293b"
        card_bg = "#1e293b"
    else:
        # Crisp light theme
        bg_color = "#ffffff"
        sec_bg_color = "#f8fafc"      # slate-50
        text_color = "#0f172a"        # slate-900
        label_color = "#64748b"       # slate-500
        primary_color = "#2563eb"     # blue-600
        border_color = "#e2e8f0"      # slate-200
        progress_bg = "#e2e8f0"       # slate-200
        input_bg = "#ffffff"
        card_bg = "#ffffff"

    # Set dynamic default Plotly template at runtime
    pio.templates.default = "plotly_dark" if theme == "dark" else "plotly"

    css = f"""
    <style>
    /* Global CSS Variable Overrides for Streamlit Component Engines */
    :root {{
        --background-color: {bg_color};
        --secondary-background-color: {sec_bg_color};
        --text-color: {text_color};
        --primary-color: {primary_color};
    }}
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    
    /* Sidebar Overrides */
    [data-testid="stSidebar"] {{
        background-color: {sec_bg_color} !important;
        border-right: 1px solid {border_color} !important;
    }}
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] .stCaption {{
        color: {text_color} !important;
    }}
    [data-testid="stSidebar"] .stRadio > label {{
        color: {text_color} !important;
    }}
    
    /* Global Button Overrides (Secondary buttons like st.button/st.download_button) */
    button[data-testid^="stBaseButton"] {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 6px !important;
    }}
    button[data-testid^="stBaseButton"]:hover {{
        border-color: {primary_color} !important;
        color: {primary_color} !important;
        background-color: {sec_bg_color} !important;
    }}
    
    /* File Uploader styling */
    [data-testid="stFileUploader"] > section {{
        background-color: {input_bg} !important;
        border: 1px dashed {border_color} !important;
        border-radius: 6px !important;
        padding: 10px !important;
    }}
    [data-testid="stFileUploader"] * {{
        color: {text_color} !important;
    }}
    
    /* Metrics Overrides */
    div.stMetric {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }}
    [data-testid="stMetricValue"] {{
        color: {text_color} !important;
        font-weight: 700 !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {label_color} !important;
    }}
    
    /* Cards (st.container(border=True)) Overrides */
    [data-testid="stVerticalBlockBorderContainer"] {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }}
    
    /* Progress Bar Overrides */
    .stProgress > div > div {{
        background-color: {progress_bg} !important;
    }}
    .stProgress > div > div > div {{
        background-color: {primary_color} !important;
    }}
    
    /* Tabs Overrides */
    button[data-baseweb="tab"] {{
        color: {label_color} !important;
        font-weight: 500 !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {primary_color} !important;
        border-bottom-color: {primary_color} !important;
        font-weight: 600 !important;
    }}
    
    /* Text/Select Inputs Overrides */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, input {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border-color: {border_color} !important;
    }}
    
    /* Expanders and other container structures */
    .streamlit-expanderHeader {{
        background-color: {sec_bg_color} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 6px;
    }}
    
    /* Success, Warning, Error alerts styling integration */
    [data-testid="stNotification"] {{
        border-radius: 8px;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def style_plotly_chart(fig):
    theme = st.session_state.settings.get("theme", "light")
    bg_color = "rgba(0,0,0,0)"  # Transparent — inherits page background
    text_color = "#f8fafc" if theme == "dark" else "#0f172a"
    grid_color = "#334155" if theme == "dark" else "#e2e8f0"

    # Use top-level font_color (magic underscore) to avoid nested dict issues in Plotly 6.x
    fig.update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font_color=text_color,
        font_family="system-ui, -apple-system, sans-serif",
        legend_font_color=text_color,
    )
    # Use dedicated axis update methods — more compatible with Plotly 5.x and 6.x
    fig.update_xaxes(
        gridcolor=grid_color,
        zerolinecolor=grid_color,
        tickfont_color=text_color,
    )
    fig.update_yaxes(
        gridcolor=grid_color,
        zerolinecolor=grid_color,
        tickfont_color=text_color,
    )
    return fig

def format_currency(amount, currency=None):
    if currency is None:
        if 'settings' in st.session_state and isinstance(st.session_state.settings, dict):
            currency = st.session_state.settings.get("currency", "USD")
        else:
            currency = "USD"
    symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "INR": "₹", "CAD": "C$", "AUD": "A$"}
    symbol = symbols.get(currency, "$")
    return f"{symbol}{amount:,.2f}"

def get_next_id(data_list):
    if not data_list:
        return 1
    return max(item.get("id", 0) for item in data_list) + 1

def calculate_account_balance(account_id, transactions):
    balance = 0
    for t in transactions:
        if t.get("account_id") == account_id:
            if t["type"] == "income":
                balance += t["amount"]
            elif t["type"] == "expense":
                balance -= t["amount"]
            elif t["type"] == "transfer":
                if t.get("from_account") == account_id:
                    balance -= t["amount"]
                if t.get("to_account") == account_id:
                    balance += t["amount"]
    return balance

def update_all_balances():
    for account in st.session_state.accounts:
        account["balance"] = calculate_account_balance(account["id"], st.session_state.transactions)
    save_accounts(st.session_state.accounts)

def get_month_range(year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    start = datetime(year, month, 1)
    end = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)
    return start, end

def filter_by_date(transactions, start_date, end_date):
    filtered = []
    if isinstance(start_date, date) and not isinstance(start_date, datetime):
        start_date = datetime.combine(start_date, datetime.min.time())
    if isinstance(end_date, date) and not isinstance(end_date, datetime):
        end_date = datetime.combine(end_date, datetime.max.time())
        
    for t in transactions:
        raw_date = t.get("date")
        if not raw_date:
            continue
        try:
            if isinstance(raw_date, datetime):
                t_date = raw_date
            elif isinstance(raw_date, date):
                t_date = datetime.combine(raw_date, datetime.min.time())
            else:
                date_str = str(raw_date).split()[0]
                t_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            if start_date <= t_date <= end_date:
                filtered.append(t)
        except Exception:
            continue
    return filtered

def get_category_spending(transactions, category, start_date, end_date):
    cat_trans = [t for t in transactions if t.get("type") == "expense" and t.get("category") == category]
    filtered = filter_by_date(cat_trans, start_date, end_date)
    return sum(float(t.get("amount", 0)) for t in filtered)

def process_recurring_transactions():
    """Auto-generate transactions from recurring items"""
    today = datetime.now().date()
    added = 0
    for rec in st.session_state.recurring:
        if not rec.get("active", True):
            continue
        last_gen = rec.get("last_generated")
        if last_gen:
            last_gen = datetime.strptime(last_gen, "%Y-%m-%d").date()
        else:
            last_gen = datetime.strptime(rec["start_date"], "%Y-%m-%d").date()
        
        frequency = rec["frequency"]  # daily, weekly, monthly, yearly
        next_date = last_gen
        
        while True:
            if frequency == "daily":
                next_date += timedelta(days=1)
            elif frequency == "weekly":
                next_date += timedelta(weeks=1)
            elif frequency == "monthly":
                new_year = next_date.year + (next_date.month // 12)
                new_month = (next_date.month % 12) + 1
                max_day = calendar.monthrange(new_year, new_month)[1]
                new_day = min(next_date.day, max_day)
                next_date = next_date.replace(year=new_year, month=new_month, day=new_day)
            elif frequency == "yearly":
                new_year = next_date.year + 1
                max_day = calendar.monthrange(new_year, next_date.month)[1]
                new_day = min(next_date.day, max_day)
                next_date = next_date.replace(year=new_year, day=new_day)
            
            if next_date > today:
                break
            
            # Add transaction
            new_trans = {
                "id": get_next_id(st.session_state.transactions),
                "date": next_date.strftime("%Y-%m-%d"),
                "type": rec["type"],
                "category": rec["category"],
                "amount": rec["amount"],
                "description": rec["description"] + " (Recurring)",
                "account_id": rec["account_id"],
                "tags": rec.get("tags", []),
                "recurring_id": rec["id"]
            }
            st.session_state.transactions.append(new_trans)
            rec["last_generated"] = next_date.strftime("%Y-%m-%d")
            added += 1
    
    if added > 0:
        save_transactions(st.session_state.transactions)
        save_recurring(st.session_state.recurring)
        update_all_balances()
    return added

# ============================================================
# PAGE: DASHBOARD
# ============================================================

def show_dashboard():
    st.title("📊 Financial Dashboard")
    
    # Process recurring transactions first
    added = process_recurring_transactions()
    if added > 0:
        st.success(f"Auto-generated {added} recurring transaction(s)")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_balance = sum(acc["balance"] for acc in st.session_state.accounts)
    
    # This month stats
    start_month, end_month = get_month_range()
    month_trans = filter_by_date(st.session_state.transactions, start_month, end_month)
    
    month_income = sum(t["amount"] for t in month_trans if t["type"] == "income")
    month_expense = sum(t["amount"] for t in month_trans if t["type"] == "expense")
    month_savings = month_income - month_expense
    
    with col1:
        st.metric("Total Balance", format_currency(total_balance), 
                 delta=format_currency(month_savings) + " this month")
    with col2:
        st.metric("Monthly Income", format_currency(month_income))
    with col3:
        st.metric("Monthly Expenses", format_currency(month_expense))
    with col4:
        savings_rate = (month_savings / month_income * 100) if month_income > 0 else 0
        st.metric("Savings Rate", f"{savings_rate:.1f}%")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Account Balances")
        if st.session_state.accounts:
            df_accounts = pd.DataFrame(st.session_state.accounts)
            fig = go.Figure(data=[go.Pie(
                labels=[f"{acc['icon']} {acc['name']}" for acc in st.session_state.accounts],
                values=[acc["balance"] for acc in st.session_state.accounts],
                hole=.4,
                marker_colors=[acc["color"] for acc in st.session_state.accounts]
            )])
            fig.update_layout(height=350, showlegend=True)
            st.plotly_chart(style_plotly_chart(fig), width='stretch')
    
    with col2:
        st.subheader("Monthly Cash Flow")
        # Last 6 months
        months = []
        incomes = []
        expenses = []
        for i in range(5, -1, -1):
            d = datetime.now() - timedelta(days=i*30)
            start, end = get_month_range(d.year, d.month)
            m_trans = filter_by_date(st.session_state.transactions, start, end)
            months.append(d.strftime("%b %Y"))
            incomes.append(sum(t["amount"] for t in m_trans if t["type"] == "income"))
            expenses.append(sum(t["amount"] for t in m_trans if t["type"] == "expense"))
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Income', x=months, y=incomes, marker_color='#2ecc71'))
        fig.add_trace(go.Bar(name='Expenses', x=months, y=expenses, marker_color='#e74c3c'))
        fig.update_layout(barmode='group', height=350)
        st.plotly_chart(style_plotly_chart(fig), width='stretch')
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Expense Breakdown (This Month)")
        expense_by_cat = defaultdict(float)
        for t in month_trans:
            if t["type"] == "expense":
                expense_by_cat[t["category"]] += t["amount"]
        
        if expense_by_cat:
            df_exp = pd.DataFrame(list(expense_by_cat.items()), columns=["Category", "Amount"])
            fig = px.pie(df_exp, values="Amount", names="Category", hole=0.3)
            fig.update_layout(height=350)
            st.plotly_chart(style_plotly_chart(fig), width='stretch')
        else:
            st.info("No expenses this month")
    
    with col2:
        st.subheader("Recent Transactions")
        recent = sorted(st.session_state.transactions, key=lambda x: x["date"], reverse=True)[:5]
        if recent:
            for t in recent:
                color = "🟢" if t["type"] == "income" else "🔴" if t["type"] == "expense" else "🔵"
                st.write(f"{color} **{t['date']}** | {t['category']} | {format_currency(t['amount'])} | {t['description']}")
        else:
            st.info("No transactions yet")
    
    # Budget Overview
    st.subheader("Budget Status (This Month)")
    budgets = st.session_state.budgets
    if budgets:
        for budget in budgets:
            spent = get_category_spending(st.session_state.transactions, budget["category"], start_month, end_month)
            limit = budget["amount"]
            pct = (spent / limit * 100) if limit > 0 else 0
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{budget['category']}**")
                st.progress(min(pct / 100, 1.0))
            with col2:
                st.write(f"{format_currency(spent)} / {format_currency(limit)}")
            with col3:
                if pct > 100:
                    st.error(f"{pct:.0f}% ⚠️")
                elif pct > 80:
                    st.warning(f"{pct:.0f}%")
                else:
                    st.success(f"{pct:.0f}%")
    else:
        st.info("No budgets set. Go to Budgets tab to create one.")
    
    # Goals Progress
    st.subheader("Financial Goals")
    goals = st.session_state.goals
    if goals:
        cols = st.columns(min(len(goals), 4))
        for idx, goal in enumerate(goals):
            with cols[idx % 4]:
                pct = (goal["current"] / goal["target"] * 100) if goal["target"] > 0 else 0
                st.metric(goal["name"], f"{pct:.1f}%", 
                         delta=f"{format_currency(goal['current'])} / {format_currency(goal['target'])}")
                st.progress(min(pct / 100, 1.0))
    else:
        st.info("No goals set. Go to Goals tab to create one.")

# ============================================================
# PAGE: TRANSACTIONS
# ============================================================

def show_transactions():
    st.title("💰 Transactions")
    
    tab1, tab2, tab3 = st.tabs(["Add Transaction", "View & Manage", "Import/Export"])
    
    with tab1:
        st.subheader("Add New Transaction")
        
        if "trans_success_msg" in st.session_state:
            st.success(st.session_state.pop("trans_success_msg"))
            
        form_id = st.session_state.get("trans_form_id", 0)
        trans_type = st.selectbox("Transaction Type", ["expense", "income", "transfer"], key=f"input_trans_type_{form_id}")
        
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.now(), key=f"input_trans_date_{form_id}")
        with col2:
            amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f", key=f"input_trans_amount_{form_id}")
        
        col1, col2 = st.columns(2)
        with col1:
            if trans_type == "income":
                category = st.selectbox("Category", st.session_state.categories.get("income", []), key=f"input_trans_cat_inc_{form_id}")
            elif trans_type == "expense":
                category = st.selectbox("Category", st.session_state.categories.get("expense", []), key=f"input_trans_cat_exp_{form_id}")
            else:
                category = st.selectbox("Category", ["Transfer"], key=f"input_trans_cat_tr_{form_id}")
        with col2:
            account_options = [(a["id"], f"{a['icon']} {a['name']}") for a in st.session_state.accounts]
            account = st.selectbox("Account", account_options, format_func=lambda x: x[1], key=f"input_trans_acc_{form_id}")
            account_id = account[0]
        
        description = st.text_input("Description", key=f"input_trans_desc_{form_id}")
        tags = st.text_input("Tags (comma separated)", key=f"input_trans_tags_{form_id}")
        
        # Transfer specific
        to_account_id = None
        if trans_type == "transfer":
            to_account_options = [(a["id"], f"{a['icon']} {a['name']}") for a in st.session_state.accounts if a["id"] != account_id]
            if to_account_options:
                to_account = st.selectbox("To Account", to_account_options, format_func=lambda x: x[1], key=f"input_trans_to_acc_{form_id}")
                to_account_id = to_account[0]
        
        if st.button("Add Transaction", type="primary"):
            if amount <= 0:
                st.error("Amount must be greater than 0")
            else:
                new_trans = {
                    "id": get_next_id(st.session_state.transactions),
                    "date": date.strftime("%Y-%m-%d"),
                    "type": trans_type,
                    "category": category,
                    "amount": amount,
                    "description": description,
                    "account_id": account_id,
                    "to_account": to_account_id,
                    "tags": [t.strip() for t in tags.split(",") if t.strip()]
                }
                st.session_state.transactions.append(new_trans)
                save_transactions(st.session_state.transactions)
                update_all_balances()
                
                # Increment form_id to generate brand new empty widgets
                st.session_state.trans_form_id = form_id + 1
                st.session_state["trans_success_msg"] = "Transaction added successfully!"
                st.rerun()
    
    with tab2:
        st.subheader("All Transactions")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filter_type = st.selectbox("Filter Type", ["All", "income", "expense", "transfer"])
        with col2:
            all_cats = ["All"] + st.session_state.categories.get("income", []) + st.session_state.categories.get("expense", []) + ["Transfer"]
            filter_cat = st.selectbox("Filter Category", all_cats)
        with col3:
            filter_start = st.date_input("From", datetime.now() - timedelta(days=30))
        with col4:
            filter_end = st.date_input("To", datetime.now())
        
        # Apply filters
        filtered = st.session_state.transactions.copy()
        if filter_type != "All":
            filtered = [t for t in filtered if t["type"] == filter_type]
        if filter_cat != "All":
            filtered = [t for t in filtered if t["category"] == filter_cat]
        filtered = filter_by_date(filtered, datetime.combine(filter_start, datetime.min.time()), 
                                datetime.combine(filter_end, datetime.max.time()))
        
        # Sort by date desc
        filtered = sorted(filtered, key=lambda x: x["date"], reverse=True)
        
        if filtered:
            df = pd.DataFrame(filtered)
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
            df["amount_fmt"] = df.apply(lambda x: format_currency(x["amount"]), axis=1)
            
            # Editable dataframe
            edited_df = st.data_editor(
                df[["id", "date", "type", "category", "amount", "description", "tags"]],
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True),
                    "date": st.column_config.DateColumn("Date"),
                    "type": st.column_config.SelectboxColumn("Type", options=["income", "expense", "transfer"]),
                    "category": st.column_config.TextColumn("Category"),
                    "amount": st.column_config.NumberColumn("Amount", format="%.2f"),
                    "description": st.column_config.TextColumn("Description"),
                    "tags": st.column_config.ListColumn("Tags")
                },
                hide_index=True,
                width='stretch',
                num_rows="dynamic",
                key="trans_data_editor"
            )
            
            # Sync edits back to transactions
            if st.button("Save Table Changes", type="primary"):
                edited_records = edited_df.to_dict('records')
                edited_map = {r['id']: r for r in edited_records if pd.notna(r['id'])}
                for t in st.session_state.transactions:
                    if t["id"] in edited_map:
                        rec = edited_map[t["id"]]
                        t_date = str(rec["date"]).split()[0] if rec["date"] else t["date"]
                        t["date"] = t_date
                        t["type"] = rec["type"]
                        t["category"] = rec["category"]
                        t["amount"] = float(rec["amount"]) if rec["amount"] is not None else 0.0
                        t["description"] = str(rec["description"]) if rec["description"] is not None else ""
                        if isinstance(rec["tags"], list):
                            t["tags"] = rec["tags"]
                save_transactions(st.session_state.transactions)
                update_all_balances()
                st.success("Transactions updated successfully!")
                st.rerun()
            
            # Delete functionality
            st.write("---")
            delete_id = st.number_input("Enter Transaction ID to Delete", min_value=1, step=1)
            if st.button("Delete Transaction", type="secondary"):
                st.session_state.transactions = [t for t in st.session_state.transactions if t["id"] != delete_id]
                save_transactions(st.session_state.transactions)
                update_all_balances()
                st.success("Transaction deleted!")
                st.rerun()
            
            # Summary
            total_income = sum(t["amount"] for t in filtered if t["type"] == "income")
            total_expense = sum(t["amount"] for t in filtered if t["type"] == "expense")
            st.write(f"**Summary:** Income: {format_currency(total_income)} | Expenses: {format_currency(total_expense)} | Net: {format_currency(total_income - total_expense)}")
        else:
            st.info("No transactions found for selected filters")
    
    with tab3:
        st.subheader("Import / Export Data")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Export to CSV**")
            if st.session_state.transactions:
                df = pd.DataFrame(st.session_state.transactions)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download Transactions CSV", csv, "transactions.csv", "text/csv")
            
            # Export all data as JSON
            all_data = {
                "transactions": st.session_state.transactions,
                "accounts": st.session_state.accounts,
                "budgets": st.session_state.budgets,
                "goals": st.session_state.goals,
                "categories": st.session_state.categories,
                "recurring": st.session_state.recurring
            }
            json_data = json.dumps(all_data, indent=2, default=str).encode('utf-8')
            st.download_button("Download Full Backup (JSON)", json_data, "finance_backup.json", "application/json")
        
        with col2:
            st.write("**Import from CSV**")
            uploaded_file = st.file_uploader("Upload CSV", type="csv")
            if uploaded_file:
                try:
                    df_import = pd.read_csv(uploaded_file)
                    st.write("Preview:")
                    st.dataframe(df_import.head())
                    if st.button("Import Transactions"):
                        for _, row in df_import.iterrows():
                            new_trans = {
                                "id": get_next_id(st.session_state.transactions),
                                "date": str(row.get("date", datetime.now().strftime("%Y-%m-%d"))),
                                "type": row.get("type", "expense"),
                                "category": row.get("category", "Other"),
                                "amount": float(row.get("amount", 0)),
                                "description": str(row.get("description", "")),
                                "account_id": int(row.get("account_id", 1)),
                                "tags": []
                            }
                            st.session_state.transactions.append(new_trans)
                        save_transactions(st.session_state.transactions)
                        update_all_balances()
                        st.success("Import successful!")
                except Exception as e:
                    st.error(f"Import failed: {e}")
            
            st.write("**Restore from Backup**")
            backup_file = st.file_uploader("Upload JSON Backup", type="json")
            if backup_file:
                try:
                    data = json.load(backup_file)
                    if st.button("Restore Data"):
                        st.session_state.transactions = data.get("transactions", [])
                        st.session_state.accounts = data.get("accounts", st.session_state.accounts)
                        st.session_state.budgets = data.get("budgets", [])
                        st.session_state.goals = data.get("goals", [])
                        st.session_state.categories = data.get("categories", st.session_state.categories)
                        st.session_state.recurring = data.get("recurring", [])
                        
                        save_transactions(st.session_state.transactions)
                        save_accounts(st.session_state.accounts)
                        save_budgets(st.session_state.budgets)
                        save_goals(st.session_state.goals)
                        save_categories(st.session_state.categories)
                        save_recurring(st.session_state.recurring)
                        update_all_balances()
                        st.success("Data restored successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Restore failed: {e}")

# ============================================================
# PAGE: ACCOUNTS
# ============================================================

def show_accounts():
    st.title("🏦 Accounts")
    
    tab1, tab2 = st.tabs(["Manage Accounts", "Account Details"])
    
    with tab1:
        st.subheader("Your Accounts")
        
        cols = st.columns(3)
        for idx, account in enumerate(st.session_state.accounts):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.write(f"### {account['icon']} {account['name']}")
                    st.write(f"**Type:** {account['type']}")
                    st.write(f"**Balance:** {format_currency(account['balance'])}")
                    st.write(f"**Currency:** {account['currency']}")
        
        st.write("---")
        st.subheader("Add New Account")
        
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Account Name")
            new_type = st.selectbox("Account Type", ["Cash", "Bank", "Credit", "Investment", "Savings", "Wallet"])
        with col2:
            new_balance = st.number_input("Initial Balance", value=0.0, step=0.01)
            new_currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY", "INR", "CAD", "AUD"])
        
        new_icon = st.selectbox("Icon", ["💵", "🏦", "💳", "💰", "📈", "👛", "🏠", "🚗"])
        new_color = st.color_picker("Color", "#3498db")
        
        if st.button("Add Account", type="primary"):
            if new_name:
                new_account = {
                    "id": get_next_id(st.session_state.accounts),
                    "name": new_name,
                    "type": new_type,
                    "balance": new_balance,
                    "currency": new_currency,
                    "color": new_color,
                    "icon": new_icon
                }
                st.session_state.accounts.append(new_account)
                save_accounts(st.session_state.accounts)
                
                # Add initial balance transaction if > 0
                if new_balance > 0:
                    init_trans = {
                        "id": get_next_id(st.session_state.transactions),
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "type": "income",
                        "category": "Other Income",
                        "amount": new_balance,
                        "description": f"Initial balance for {new_name}",
                        "account_id": new_account["id"],
                        "tags": ["initial"]
                    }
                    st.session_state.transactions.append(init_trans)
                    save_transactions(st.session_state.transactions)
                
                update_all_balances()
                st.success("Account created!")
                st.rerun()
            else:
                st.error("Account name is required")
    
    with tab2:
        st.subheader("Account Transaction History")
        
        selected_account = st.selectbox("Select Account", 
                                       [(a["id"], f"{a['icon']} {a['name']}") for a in st.session_state.accounts],
                                       format_func=lambda x: x[1])
        account_id = selected_account[0]
        
        account_trans = [t for t in st.session_state.transactions if t.get("account_id") == account_id or t.get("to_account") == account_id]
        account_trans = sorted(account_trans, key=lambda x: x["date"], reverse=True)
        
        if account_trans:
            df = pd.DataFrame(account_trans)
            cols_to_show = [c for c in ["date", "type", "category", "amount", "description"] if c in df.columns]
            st.dataframe(df[cols_to_show], width='stretch')
            
            # Balance over time
            df["parsed_date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["parsed_date"]).sort_values("parsed_date")
            running_balance = []
            bal = 0
            for _, row in df.iterrows():
                amt = float(row.get("amount", 0))
                t_type = row.get("type")
                if t_type == "income":
                    bal += amt
                elif t_type == "expense":
                    bal -= amt
                elif t_type == "transfer":
                    if row.get("account_id") == account_id:
                        bal -= amt
                    if row.get("to_account") == account_id:
                        bal += amt
                running_balance.append(bal)
            df["balance"] = running_balance
            
            if not df.empty:
                fig = px.line(df, x="parsed_date", y="balance", title="Balance Over Time")
                st.plotly_chart(style_plotly_chart(fig), width='stretch')
        else:
            st.info("No transactions for this account")

# ============================================================
# PAGE: BUDGETS
# ============================================================

def show_budgets():
    st.title("📋 Budgets")
    
    tab1, tab2 = st.tabs(["Manage Budgets", "Budget Analysis"])
    
    with tab1:
        st.subheader("Create Budget")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            budget_cat = st.selectbox("Category", st.session_state.categories.get("expense", []))
        with col2:
            budget_amount = st.number_input("Monthly Limit", min_value=0.0, step=10.0)
        with col3:
            budget_alert = st.slider("Alert Threshold (%)", 50, 100, 80)
        
        if st.button("Create Budget", type="primary"):
            # Check if budget exists for this category
            existing = [b for b in st.session_state.budgets if b["category"] == budget_cat]
            if existing:
                st.error(f"Budget for {budget_cat} already exists. Delete it first to update.")
            else:
                new_budget = {
                    "id": get_next_id(st.session_state.budgets),
                    "category": budget_cat,
                    "amount": budget_amount,
                    "alert_threshold": budget_alert,
                    "created": datetime.now().strftime("%Y-%m-%d")
                }
                st.session_state.budgets.append(new_budget)
                save_budgets(st.session_state.budgets)
                st.success(f"Budget created for {budget_cat}")
                st.rerun()
        
        st.write("---")
        st.subheader("Current Budgets")
        
        start_month, end_month = get_month_range()
        
        if st.session_state.budgets:
            for budget in st.session_state.budgets:
                spent = get_category_spending(st.session_state.transactions, budget["category"], start_month, end_month)
                limit = budget["amount"]
                pct = (spent / limit * 100) if limit > 0 else 0
                alert = budget.get("alert_threshold", 80)
                
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    with col1:
                        st.write(f"**{budget['category']}**")
                        st.write(f"Limit: {format_currency(limit)}")
                    with col2:
                        st.write(f"Spent: {format_currency(spent)}")
                        st.write(f"Remaining: {format_currency(limit - spent)}")
                    with col3:
                        if pct > 100:
                            st.error(f"{pct:.0f}%")
                        elif pct > alert:
                            st.warning(f"{pct:.0f}%")
                        else:
                            st.success(f"{pct:.0f}%")
                    with col4:
                        if st.button("Delete", key=f"del_budget_{budget['id']}"):
                            st.session_state.budgets = [b for b in st.session_state.budgets if b["id"] != budget["id"]]
                            save_budgets(st.session_state.budgets)
                            st.rerun()
                    
                    st.progress(min(pct / 100, 1.0))
        else:
            st.info("No budgets created yet")
    
    with tab2:
        st.subheader("Budget vs Actual Spending")
        
        # Monthly selector
        months = []
        for i in range(5, -1, -1):
            d = datetime.now() - timedelta(days=i*30)
            months.append((d.year, d.month, d.strftime("%B %Y")))
        
        selected_month = st.selectbox("Select Month", months, format_func=lambda x: x[2])
        year, month, _ = selected_month
        start, end = get_month_range(year, month)
        
        if st.session_state.budgets:
            cats = [b["category"] for b in st.session_state.budgets]
            budgets = [b["amount"] for b in st.session_state.budgets]
            actuals = [get_category_spending(st.session_state.transactions, cat, start, end) for cat in cats]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Budget', x=cats, y=budgets, marker_color='#3498db'))
            fig.add_trace(go.Bar(name='Actual', x=cats, y=actuals, marker_color='#e74c3c'))
            fig.update_layout(barmode='group', height=500, title="Budget vs Actual")
            st.plotly_chart(style_plotly_chart(fig), width='stretch')
            
            # Overspending alert
            overspent = [(cat, act, bud) for cat, act, bud in zip(cats, actuals, budgets) if act > bud]
            if overspent:
                st.warning("⚠️ Overspending Alert!")
                for cat, act, bud in overspent:
                    st.write(f"- **{cat}**: Spent {format_currency(act)} vs Budget {format_currency(bud)} (Over by {format_currency(act - bud)})")
        else:
            st.info("Create budgets first to see analysis")

# ============================================================
# PAGE: GOALS
# ============================================================

def show_goals():
    st.title("🎯 Financial Goals")
    
    tab1, tab2 = st.tabs(["Manage Goals", "Goal Progress"])
    
    with tab1:
        st.subheader("Create New Goal")
        
        col1, col2 = st.columns(2)
        with col1:
            goal_name = st.text_input("Goal Name")
            goal_target = st.number_input("Target Amount", min_value=0.0, step=100.0)
        with col2:
            goal_current = st.number_input("Current Amount", min_value=0.0, step=10.0)
            goal_deadline = st.date_input("Target Date", datetime.now() + timedelta(days=365))
        
        goal_icon = st.selectbox("Icon", ["🏠", "🚗", "✈️", "🎓", "💍", "🏖️", "💰", "📱", "💻", "🎯"])
        goal_color = st.color_picker("Color", "#9b59b6")
        
        if st.button("Create Goal", type="primary"):
            if goal_name and goal_target > 0:
                new_goal = {
                    "id": get_next_id(st.session_state.goals),
                    "name": goal_name,
                    "target": goal_target,
                    "current": goal_current,
                    "deadline": goal_deadline.strftime("%Y-%m-%d"),
                    "icon": goal_icon,
                    "color": goal_color,
                    "created": datetime.now().strftime("%Y-%m-%d")
                }
                st.session_state.goals.append(new_goal)
                save_goals(st.session_state.goals)
                st.success("Goal created!")
                st.rerun()
            else:
                st.error("Goal name and target amount are required")
        
        st.write("---")
        st.subheader("Your Goals")
        
        if st.session_state.goals:
            for goal in st.session_state.goals:
                pct = (goal["current"] / goal["target"] * 100) if goal["target"] > 0 else 0
                try:
                    deadline_dt = datetime.strptime(str(goal["deadline"]).split()[0], "%Y-%m-%d")
                    days_left = (deadline_dt - datetime.now()).days
                except Exception:
                    days_left = 0
                
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    with col1:
                        st.write(f"### {goal['icon']} {goal['name']}")
                        st.write(f"Target: {format_currency(goal['target'])}")
                    with col2:
                        st.write(f"Current: {format_currency(goal['current'])}")
                        st.write(f"Deadline: {goal['deadline']} ({days_left} days left)")
                    with col3:
                        st.write(f"### {pct:.1f}%")
                    with col4:
                        if st.button("Update", key=f"update_goal_{goal['id']}"):
                            st.session_state[f"edit_goal_{goal['id']}"] = True
                        if st.button("Delete", key=f"del_goal_{goal['id']}"):
                            st.session_state.goals = [g for g in st.session_state.goals if g["id"] != goal["id"]]
                            save_goals(st.session_state.goals)
                            st.rerun()
                    
                    st.progress(min(pct / 100, 1.0))
                    
                    # Quick update
                    if st.session_state.get(f"edit_goal_{goal['id']}", False):
                        add_amount = st.number_input(f"Add to {goal['name']}", min_value=0.0, step=10.0, key=f"add_{goal['id']}")
                        if st.button("Save", key=f"save_{goal['id']}"):
                            goal["current"] += add_amount
                            save_goals(st.session_state.goals)
                            st.session_state[f"edit_goal_{goal['id']}"] = False
                            st.rerun()
        else:
            st.info("No goals created yet. Start planning your financial future!")
    
    with tab2:
        st.subheader("Goal Timeline")
        
        if st.session_state.goals:
            fig = go.Figure()
            for goal in st.session_state.goals:
                fig.add_trace(go.Bar(
                    name=goal["name"],
                    x=[goal["name"]],
                    y=[goal["target"]],
                    marker_color='lightgray'
                ))
                fig.add_trace(go.Bar(
                    name=f"{goal['name']} (Current)",
                    x=[goal["name"]],
                    y=[goal["current"]],
                    marker_color=goal.get("color", "#3498db")
                ))
            fig.update_layout(barmode='overlay', height=400, title="Target vs Current")
            st.plotly_chart(style_plotly_chart(fig), width='stretch')
            
            # Savings rate needed
            st.subheader("Required Monthly Savings")
            for goal in st.session_state.goals:
                remaining = goal["target"] - goal["current"]
                try:
                    deadline_dt = datetime.strptime(str(goal["deadline"]).split()[0], "%Y-%m-%d")
                    days_left = max((deadline_dt - datetime.now()).days, 1)
                except Exception:
                    days_left = 30
                months_left = days_left / 30
                monthly_needed = remaining / months_left if months_left > 0 else 0
                
                st.write(f"**{goal['icon']} {goal['name']}**: {format_currency(monthly_needed)}/month needed to reach {format_currency(goal['target'])} by {goal['deadline']}")
        else:
            st.info("No goals to analyze")

# ============================================================
# PAGE: RECURRING
# ============================================================

def show_recurring():
    st.title("🔄 Recurring Transactions")
    
    st.subheader("Set Up Recurring Transaction")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        rec_type = st.selectbox("Type", ["expense", "income"])
    with col2:
        if rec_type == "income":
            rec_cat = st.selectbox("Category", st.session_state.categories.get("income", []))
        else:
            rec_cat = st.selectbox("Category", st.session_state.categories.get("expense", []))
    with col3:
        rec_amount = st.number_input("Amount", min_value=0.0, step=10.0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        rec_desc = st.text_input("Description")
    with col2:
        rec_freq = st.selectbox("Frequency", ["daily", "weekly", "monthly", "yearly"])
    with col3:
        rec_account = st.selectbox("Account", 
                                   [(a["id"], f"{a['icon']} {a['name']}") for a in st.session_state.accounts],
                                   format_func=lambda x: x[1])
    
    rec_start = st.date_input("Start Date", datetime.now())
    rec_tags = st.text_input("Tags (comma separated)")
    
    if st.button("Add Recurring", type="primary"):
        new_rec = {
            "id": get_next_id(st.session_state.recurring),
            "type": rec_type,
            "category": rec_cat,
            "amount": rec_amount,
            "description": rec_desc,
            "frequency": rec_freq,
            "account_id": rec_account[0],
            "start_date": rec_start.strftime("%Y-%m-%d"),
            "tags": [t.strip() for t in rec_tags.split(",") if t.strip()],
            "active": True,
            "last_generated": None
        }
        st.session_state.recurring.append(new_rec)
        save_recurring(st.session_state.recurring)
        st.success("Recurring transaction added!")
        st.rerun()
    
    st.write("---")
    st.subheader("Active Recurring Transactions")
    
    if st.session_state.recurring:
        for rec in st.session_state.recurring:
            status = "✅ Active" if rec.get("active", True) else "❌ Inactive"
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.write(f"**{rec['description']}** ({rec['category']})")
                    st.write(f"Amount: {format_currency(rec['amount'])} | Freq: {rec['frequency']}")
                with col2:
                    st.write(f"Start: {rec['start_date']}")
                    st.write(f"Status: {status}")
                with col3:
                    st.write(f"Last Generated: {rec.get('last_generated', 'Never')}")
                with col4:
                    if st.button("Toggle", key=f"toggle_{rec['id']}"):
                        rec["active"] = not rec.get("active", True)
                        save_recurring(st.session_state.recurring)
                        st.rerun()
                    if st.button("Delete", key=f"del_rec_{rec['id']}"):
                        st.session_state.recurring = [r for r in st.session_state.recurring if r["id"] != rec["id"]]
                        save_recurring(st.session_state.recurring)
                        st.rerun()
    else:
        st.info("No recurring transactions set up")

# ============================================================
# PAGE: REPORTS & ANALYTICS
# ============================================================

def show_reports():
    st.title("📈 Reports & Analytics")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Spending Trends", "Income Analysis", "Category Deep Dive", "Yearly Summary"])
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        report_start = st.date_input("Start Date", datetime.now() - timedelta(days=365))
    with col2:
        report_end = st.date_input("End Date", datetime.now())
    
    filtered = filter_by_date(st.session_state.transactions, 
                            datetime.combine(report_start, datetime.min.time()),
                            datetime.combine(report_end, datetime.max.time()))
    
    with tab1:
        st.subheader("Spending Trends Over Time")
        
        if filtered:
            df = pd.DataFrame(filtered)
            df["date"] = pd.to_datetime(df["date"])
            
            # Daily spending
            daily = df[df["type"] == "expense"].groupby("date")["amount"].sum().reset_index()
            if not daily.empty:
                fig = px.line(daily, x="date", y="amount", title="Daily Spending")
                fig.update_layout(height=400)
                st.plotly_chart(style_plotly_chart(fig), width='stretch')
            
            # Monthly trend
            df["month"] = df["date"].dt.to_period("M").astype(str)
            monthly_exp = df[df["type"] == "expense"].groupby("month")["amount"].sum().reset_index()
            monthly_inc = df[df["type"] == "income"].groupby("month")["amount"].sum().reset_index()
            
            fig = go.Figure()
            if not monthly_exp.empty:
                fig.add_trace(go.Bar(name='Expenses', x=monthly_exp["month"], y=monthly_exp["amount"], marker_color='#e74c3c'))
            if not monthly_inc.empty:
                fig.add_trace(go.Bar(name='Income', x=monthly_inc["month"], y=monthly_inc["amount"], marker_color='#2ecc71'))
            fig.update_layout(barmode='group', height=400, title="Monthly Income vs Expenses")
            st.plotly_chart(style_plotly_chart(fig), width='stretch')
        else:
            st.info("No data for selected period")
    
    with tab2:
        st.subheader("Income Analysis")
        
        income_trans = [t for t in filtered if t["type"] == "income"]
        if income_trans:
            df = pd.DataFrame(income_trans)
            
            # By category
            cat_income = df.groupby("category")["amount"].sum().reset_index()
            fig = px.pie(cat_income, values="amount", names="category", title="Income by Category")
            st.plotly_chart(style_plotly_chart(fig), width='stretch')
            
            # Income trend
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            fig = px.bar(df, x="date", y="amount", color="category", title="Income Timeline")
            st.plotly_chart(style_plotly_chart(fig), width='stretch')
        else:
            st.info("No income data for selected period")
    
    with tab3:
        st.subheader("Category Deep Dive")
        
        expense_trans = [t for t in filtered if t.get("type") == "expense"]
        if expense_trans:
            df = pd.DataFrame(expense_trans)
            
            all_cats = sorted(df["category"].unique()) if "category" in df.columns else []
            if all_cats:
                selected_cat = st.selectbox("Select Category", all_cats)
                
                cat_df = df[df["category"] == selected_cat].copy()
                cat_df["date"] = pd.to_datetime(cat_df["date"], errors="coerce")
                
                total_spent = cat_df['amount'].sum() if "amount" in cat_df.columns else 0
                mean_spent = cat_df['amount'].mean() if "amount" in cat_df.columns else 0
                st.write(f"Total spent on {selected_cat}: {format_currency(total_spent)}")
                st.write(f"Average per transaction: {format_currency(mean_spent)}")
                st.write(f"Number of transactions: {len(cat_df)}")
                
                hover_cols = [c for c in ["description"] if c in cat_df.columns]
                has_positive = "amount" in cat_df.columns and (cat_df["amount"] > 0).all()
                if has_positive:
                    fig = px.scatter(cat_df, x="date", y="amount", size="amount", 
                                   hover_data=hover_cols, title=f"{selected_cat} Spending Pattern")
                else:
                    fig = px.scatter(cat_df, x="date", y="amount", 
                                   hover_data=hover_cols, title=f"{selected_cat} Spending Pattern")
                st.plotly_chart(style_plotly_chart(fig), width='stretch')
                
                # Top merchants/descriptions
                if "description" in cat_df.columns and "amount" in cat_df.columns:
                    st.subheader("Top Spending in this Category")
                    top_desc = cat_df.groupby("description")["amount"].sum().sort_values(ascending=False).head(10)
                    st.bar_chart(top_desc)
        else:
            st.info("No expense data for selected period")
    
    with tab4:
        st.subheader("Yearly Summary")
        
        current_year = datetime.now().year
        years = list(range(current_year - 2, current_year + 1))
        selected_year = st.selectbox("Select Year", years)
        
        year_trans = [t for t in st.session_state.transactions if str(t.get("date", "")).startswith(str(selected_year))]
        
        if year_trans:
            # Monthly breakdown
            monthly_data = defaultdict(lambda: {"income": 0, "expense": 0})
            for t in year_trans:
                parts = str(t.get("date", "")).split("-")
                if len(parts) >= 2 and parts[1].isdigit():
                    month = int(parts[1])
                    if 1 <= month <= 12:
                        amt = float(t.get("amount", 0))
                        if t.get("type") == "income":
                            monthly_data[month]["income"] += amt
                        elif t.get("type") == "expense":
                            monthly_data[month]["expense"] += amt
            
            months = list(range(1, 13))
            incomes = [monthly_data[m]["income"] for m in months]
            expenses = [monthly_data[m]["expense"] for m in months]
            savings = [i - e for i, e in zip(incomes, expenses)]
            
            fig = make_subplots(rows=2, cols=1, subplot_titles=("Monthly Cash Flow", "Cumulative Savings"))
            
            fig.add_trace(go.Bar(name='Income', x=months, y=incomes, marker_color='#2ecc71'), row=1, col=1)
            fig.add_trace(go.Bar(name='Expenses', x=months, y=expenses, marker_color='#e74c3c'), row=1, col=1)
            
            cum_savings = []
            cum = 0
            for s in savings:
                cum += s
                cum_savings.append(cum)
            fig.add_trace(go.Scatter(name='Cumulative Savings', x=months, y=cum_savings, 
                                    marker_color='#3498db', fill='tozeroy'), row=2, col=1)
            
            fig.update_layout(height=600, showlegend=True)
            st.plotly_chart(style_plotly_chart(fig), width='stretch')
            
            # Year totals
            total_income = sum(incomes)
            total_expense = sum(expenses)
            total_savings = total_income - total_expense
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", format_currency(total_income))
            col2.metric("Total Expenses", format_currency(total_expense))
            col3.metric("Net Savings", format_currency(total_savings))
        else:
            st.info("No data for selected year")

# ============================================================
# PAGE: CATEGORIES & SETTINGS
# ============================================================

def show_settings():
    st.title("⚙️ Settings & Categories")
    
    tab1, tab2, tab3 = st.tabs(["Categories", "App Settings", "Data Management"])
    
    with tab1:
        st.subheader("Manage Categories")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Income Categories**")
            for cat in st.session_state.categories.get("income", []):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"• {cat}")
                with col_b:
                    if st.button("Remove", key=f"rem_inc_{cat}"):
                        st.session_state.categories["income"].remove(cat)
                        save_categories(st.session_state.categories)
                        st.rerun()
            
            new_inc_cat = st.text_input("Add Income Category")
            if st.button("Add Income Category") and new_inc_cat:
                if new_inc_cat not in st.session_state.categories["income"]:
                    st.session_state.categories["income"].append(new_inc_cat)
                    save_categories(st.session_state.categories)
                    st.rerun()
        
        with col2:
            st.write("**Expense Categories**")
            for cat in st.session_state.categories.get("expense", []):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"• {cat}")
                with col_b:
                    if st.button("Remove", key=f"rem_exp_{cat}"):
                        st.session_state.categories["expense"].remove(cat)
                        save_categories(st.session_state.categories)
                        st.rerun()
            
            new_exp_cat = st.text_input("Add Expense Category")
            if st.button("Add Expense Category") and new_exp_cat:
                if new_exp_cat not in st.session_state.categories["expense"]:
                    st.session_state.categories["expense"].append(new_exp_cat)
                    save_categories(st.session_state.categories)
                    st.rerun()
    
    with tab2:
        st.subheader("Application Settings")
        
        currency = st.selectbox("Default Currency", ["USD", "EUR", "GBP", "JPY", "INR", "CAD", "AUD"], 
                               index=["USD", "EUR", "GBP", "JPY", "INR", "CAD", "AUD"].index(st.session_state.settings.get("currency", "USD")))
        date_format = st.selectbox("Date Format", ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"])
        
        theme = st.selectbox("Theme Mode", ["light", "dark"],
                             index=["light", "dark"].index(st.session_state.settings.get("theme", "light")))
        
        if st.button("Save Settings", type="primary"):
            st.session_state.settings = {"currency": currency, "date_format": date_format, "theme": theme}
            save_settings(st.session_state.settings)
            st.success("Settings saved!")
            st.rerun()
    
    with tab3:
        st.subheader("Data Management")
        
        st.warning("⚠️ These actions cannot be undone!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Clear Transactions**")
            confirm_clear = st.checkbox("Confirm delete all transactions")
            if st.button("Clear All Transactions", type="secondary", disabled=not confirm_clear):
                st.session_state.transactions = []
                save_transactions([])
                update_all_balances()
                st.success("All transactions cleared")
                st.rerun()
        
        with col2:
            st.write("**Reset Application**")
            confirm_reset = st.checkbox("Confirm reset ALL data")
            if st.button("Reset All Data", type="secondary", disabled=not confirm_reset):
                st.session_state.transactions = []
                st.session_state.budgets = []
                st.session_state.goals = []
                st.session_state.recurring = []
                st.session_state.accounts = [
                    {"id": 1, "name": "Cash", "type": "Cash", "balance": 0.0, "currency": "USD", "color": "#2ecc71", "icon": "💵"},
                    {"id": 2, "name": "Bank Account", "type": "Bank", "balance": 0.0, "currency": "USD", "color": "#3498db", "icon": "🏦"},
                    {"id": 3, "name": "Credit Card", "type": "Credit", "balance": 0.0, "currency": "USD", "color": "#e74c3c", "icon": "💳"},
                ]
                st.session_state.categories = {
                    "income": DEFAULT_INCOME_CATEGORIES,
                    "expense": DEFAULT_EXPENSE_CATEGORIES
                }
                
                save_transactions([])
                save_budgets([])
                save_goals([])
                save_recurring([])
                save_accounts(st.session_state.accounts)
                save_categories(st.session_state.categories)
                st.success("All data reset to defaults")
                st.rerun()
        
        st.write("---")
        st.write("**Data Storage Location:** `Browser localStorage (Local Machine)`")
        st.write("Your data is stored privately and securely inside your browser's local storage on this device. It is saved automatically and persists even if you close the tab or restart the device.")

# ============================================================
# MAIN APP
# ============================================================

def main():
    st.set_page_config(
        page_title="Personal Finance Manager",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state first so settings are loaded
    init_session_state()

    # Non-blocking background data load from browser local storage on startup
    res = local_storage(action="load", key="init_loader")
    if not st.session_state.get("data_loaded", False):
        if res is not None:
            if res.get("status") == "loaded" and res.get("data"):
                try:
                    loaded_data = json.loads(res["data"])
                    st.session_state.transactions = loaded_data.get("transactions", [])
                    st.session_state.accounts     = loaded_data.get("accounts", st.session_state.accounts)
                    st.session_state.budgets      = loaded_data.get("budgets", [])
                    st.session_state.goals        = loaded_data.get("goals", [])
                    st.session_state.categories   = loaded_data.get("categories", st.session_state.categories)
                    st.session_state.recurring    = loaded_data.get("recurring", [])
                    st.session_state.settings     = loaded_data.get("settings", st.session_state.settings)
                    update_all_balances()
                except Exception as e:
                    pass
            st.session_state.data_loaded = True
            st.rerun()

    # Inject theme variables and layout CSS dynamically
    apply_theme_css()
    
    # Sidebar Navigation
    with st.sidebar:
        st.title("💰 Finance Manager")
        st.write("---")
        
        page = st.radio("Navigation", [
            "📊 Dashboard",
            "💰 Transactions",
            "🏦 Accounts",
            "📋 Budgets",
            "🎯 Goals",
            "🔄 Recurring",
            "📈 Reports",
            "⚙️ Settings"
        ])
        
        # Theme switcher dropdown
        st.write("---")
        theme_options = ["Light Mode", "Dark Mode"]
        current_theme = st.session_state.settings.get("theme", "light")
        theme_index = 0 if current_theme == "light" else 1
        selected_theme_label = st.selectbox(
            "Theme Mode",
            theme_options,
            index=theme_index,
            key="sidebar_theme_selector"
        )
        new_theme = "light" if selected_theme_label == "Light Mode" else "dark"
        if new_theme != current_theme:
            st.session_state.settings["theme"] = new_theme
            save_settings(st.session_state.settings)
            st.rerun()
        
        # ── 💾 My Data (per-user persistence) ─────────────────────────────
        st.write("---")
        st.markdown("**💾 My Data**")
        st.caption("Your data is private to your session. Download a backup to keep it across visits.")

        # Build full backup payload
        backup_payload = json.dumps({
            "transactions": st.session_state.transactions,
            "accounts":     st.session_state.accounts,
            "budgets":      st.session_state.budgets,
            "goals":        st.session_state.goals,
            "categories":   st.session_state.categories,
            "recurring":    st.session_state.recurring,
            "settings":     st.session_state.settings,
        }, indent=2, default=str).encode("utf-8")

        st.download_button(
            label="📥 Download My Data",
            data=backup_payload,
            file_name=f"my_finance_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True,
        )

        uploaded = st.file_uploader("📤 Load My Data", type="json", label_visibility="collapsed")
        if uploaded is not None and not st.session_state.get("_upload_processed_" + uploaded.name, False):
            try:
                data = json.load(uploaded)
                st.session_state.transactions = data.get("transactions", [])
                st.session_state.accounts     = data.get("accounts", st.session_state.accounts)
                st.session_state.budgets      = data.get("budgets", [])
                st.session_state.goals        = data.get("goals", [])
                st.session_state.categories   = data.get("categories", st.session_state.categories)
                st.session_state.recurring    = data.get("recurring", [])
                st.session_state.settings     = data.get("settings", st.session_state.settings)
                update_all_balances()
                st.session_state["_upload_processed_" + uploaded.name] = True
                st.success("✅ Data loaded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to load data: {e}")

        # ── Quick Stats ────────────────────────────────────────────────────
        st.write("---")
        st.write("**Quick Stats**")
        total_balance = sum(acc["balance"] for acc in st.session_state.accounts)
        st.write(f"Total: {format_currency(total_balance)}")

        # Show top spending category this month
        start_month, end_month = get_month_range()
        month_trans = filter_by_date(st.session_state.transactions, start_month, end_month)
        expense_by_cat = defaultdict(float)
        for t in month_trans:
            if t["type"] == "expense":
                expense_by_cat[t["category"]] += t["amount"]
        if expense_by_cat:
            top_cat = max(expense_by_cat, key=expense_by_cat.get)
            st.write(f"Top Spend: {top_cat}")
    
    # Route to page
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "💰 Transactions":
        show_transactions()
    elif page == "🏦 Accounts":
        show_accounts()
    elif page == "📋 Budgets":
        show_budgets()
    elif page == "🎯 Goals":
        show_goals()
    elif page == "🔄 Recurring":
        show_recurring()
    elif page == "📈 Reports":
        show_reports()
    elif page == "⚙️ Settings":
        show_settings()

    # Trigger auto-save if there are unsaved changes
    if st.session_state.get("trigger_save", False):
        st.session_state.trigger_save = False
        trigger_auto_save()

if __name__ == "__main__":
    main()
