import streamlit as st
import pandas as pd
import os
from datetime import datetime

FILE_NAME = "expenses.csv"


# Helper function to add an expense to our CSV file
def adds_expense(date, amount, category, description):
    """Adds a new expense to the file or creates the file if it doesn't exist."""

    try:
        expense = {
            "Date": date,
            "Amount": amount,
            "Category": category,
            "Description": description,
        }

        # Check if the file exists already, if yes, add to it
        if os.path.exists(FILE_NAME):
            df = pd.read_csv(FILE_NAME)
            df = pd.concat([df, pd.DataFrame([expense])], ignore_index=True)

        else:
            # Create a new DataFrame if the file's missing
            df = pd.DataFrame([expense])

        # Save the DataFrame back to the file
        df.to_csv(FILE_NAME, index=False)

        return "Expense added successfully!"

    except Exception as e:
        # Not sure what could go wrong, but just in case
        return f"Error adding expense: {str(e)}"


# Function to create a report of all expenses grouped by category/month
def view_report():
    """Generates a report showing total spending per category for each month."""

    try:
        if not os.path.exists(FILE_NAME):
            return "No expenses recorded yet!", None

        df = pd.read_csv(FILE_NAME)

        # Convert the 'Date' column to proper datetime, handle errors too
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Drop rows where the date isn't valid, gotta clean up bad data
        df = df.dropna(subset=["Date"])

        # Add a column for the month based on the date
        df["Month"] = df["Date"].dt.to_period("M")

        # Make sure the 'Amount' column is numeric, just in case someone entered weird stuff
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

        # Drop rows where the amount isn't valid (e.g., if it's NaN)
        df = df.dropna(subset=["Amount"])

        # Group by month and category, then sum the amounts
        report = df.groupby(["Month", "Category"])["Amount"].sum().unstack(fill_value=0)

        return None, report

    except Exception as e:
        # Something went wrong while generating the report
        return f"Error generating report: {str(e)}", None


# Function to predict next month's expenses based on history
def predict_the_next_month():
    """Predicts expenses for next month by averaging past months' spending."""

    try:
        if not os.path.exists(FILE_NAME):
            return "No expenses recorded yet!"

        df = pd.read_csv(FILE_NAME)

        # Convert the 'Date' column to datetime
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Drop bad rows (invalid dates)
        df = df.dropna(subset=["Date"])

        # Add a month column for easier grouping
        df["Month"] = df["Date"].dt.to_period("M")

        # Make sure 'Amount' is numeric
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

        # Remove rows with invalid amounts
        df = df.dropna(subset=["Amount"])

        # Group by month and calculate total spending for each month
        monthly_totals = df.groupby("Month")["Amount"].sum()

        # Just take the average as the prediction
        prediction = monthly_totals.mean()

        return f"Based on your spending history, your predicted total expenses for next month are: ${prediction:.2f}"

    except Exception as e:
        # Better safe than sorry, catch errors here
        return f"Error predicting expenses: {str(e)}"


# Calculates how much of the monthly budget remains after savings
def calculate_the_monthly_budget(yearly_income, savings_goal):
    """Calculates monthly income and leftover budget after savings."""

    monthly_income = yearly_income / 12  # divide income into months
    remaining_budget = monthly_income - savings_goal  # subtract savings

    return monthly_income, remaining_budget


# Streamlit stuff starts here
st.title("Expense Tracker with Budgeting")
st.write("Track your expenses, manage your budget, and plan savings.")

# Sidebar for user inputs like income and savings goals
st.sidebar.header("Set Your Budget")
yearly_income = st.sidebar.number_input("Enter your yearly income ($):", min_value=0.0, step=1000.0, format="%.2f")
savings_goal = st.sidebar.number_input("Enter your monthly savings goal ($):", min_value=0.0, step=50.0, format="%.2f")

if yearly_income > 0:
    # Break down yearly income into months and calculate leftover
    monthly_income, remaining_budget = calculate_the_monthly_budget(yearly_income, savings_goal)

    st.sidebar.success(f"Your monthly income: ${monthly_income:.2f}")
    st.sidebar.success(f"Budget after savings: ${remaining_budget:.2f}")

else:
    st.sidebar.warning("Please enter your yearly income to calculate your budget.")

# Tabs for adding expenses, viewing reports, and predicting expenses
tab1, tab2, tab3 = st.tabs(["Add Expense", "View Report", "Predict Expenses"])

with tab1:
    st.header("Add a New Expense")
    date = st.date_input("Date", value=datetime.now().date())
    amount = st.number_input("Expense Amount", min_value=0.0, format="%.2f")

    # Dropdown for selecting the category of the expense
    category = st.selectbox(
        "Category",
        [
            "Food",
            "Transport",
            "Entertainment",
            "Shopping",
            "Bills",
            "Rent",
            "Healthcare",
            "Education",
            "Travel",
            "Savings",
            "Other"
        ]
    )

    description = st.text_input("Description", placeholder="Optional")

    if st.button("Add Expense"):
        message = adds_expense(date, amount, category, description)

        if "successfully" in message:
            st.success(message)

        else:
            st.error(message)

with tab2:
    st.header("Monthly Expense Report")

    try:
        error, report = view_report()
        if error:
            st.warning(error)

        else:
            st.write("Here is your monthly report:")
            st.dataframe(report)

    except Exception as e:
        st.error(f"An error occurred while generating the report: {str(e)}")

with tab3:
    st.header("Predict Next Month's Expenses")

    try:
        prediction = predict_the_next_month()
        if "Error" in prediction:
            st.error(prediction)

        else:
            st.info(prediction)

    except Exception as e:
        st.error(f"An error occurred while predicting expenses: {str(e)}")

# Show remaining monthly budget
if yearly_income > 0:
    st.header("Remaining Monthly Budget")
    total_expenses = 0

    try:
        if os.path.exists(FILE_NAME):
            df = pd.read_csv(FILE_NAME)
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df["Month"] = df["Date"].dt.to_period("M")
            current_month = datetime.now().strftime("%Y-%m")
            total_expenses = df[df["Month"].astype(str) == current_month]["Amount"].sum()

        remaining_budget_after_expenses = remaining_budget - total_expenses
        st.success(f"Remaining budget for this month: ${remaining_budget_after_expenses:.2f}")

    except Exception as e:
        st.error(f"An error occurred while calculating the remaining budget: {str(e)}")

