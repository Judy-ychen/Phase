import streamlit as st
import requests
from datetime import datetime, timedelta
import time
from datetime import date

# Backend URL
BASE_URL = "http://127.0.0.1:5000"

# Initialize Session State
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "login"
    
# Helper function to fetch current phase and recommendations
def fetch_current_phase(selected_date=None):
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    payload = {
        "period_start": st.session_state.get("period_start"),
        "period_end": st.session_state.get("period_end"),
    }
    if selected_date:
        payload["selected_date"] = selected_date.strftime("%Y-%m-%d")
        endpoint = "select-date"
    else:
        endpoint = "menstrual-phase"

    response = requests.post(
        f"{BASE_URL}/{endpoint}",
        json=payload,
        headers=headers,
    )
    if response.status_code == 200:
        phase_data = response.json()
        return phase_data.get("phase"), phase_data.get("food_recommendations"), phase_data.get("exercise_recommendations"), phase_data.get("lifestyle_tip")
    else:
        return "Unknown", {}, {}, {}

# Helper Function to Handle Authentication
def authenticate(action, payload):
    url = f"{BASE_URL}/{action}"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Navigation Helper
def navigate_to(page_name):
    st.session_state["page"] = page_name
    
# Helper Function for Navigation
def set_page(page):
    if "previous_page" in st.session_state:
        st.session_state.previous_page = st.session_state.page
    else:
        st.session_state.previous_page = "dashboard_page"
    st.session_state.page = page

# Main App Logic
def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "dashboard_page"
    if "previous_page" not in st.session_state:
        st.session_state["previous_page"] = "dashboard_page"
        
    if st.session_state["page"] == "login":
        login_page()
    elif st.session_state["page"] == "signup":
        signup_page()
    elif st.session_state["page"] == "main":
        dashboard_page()
    elif st.session_state["page"] == "record_page":
        record_page()
    elif st.session_state["page"] == "logout":
        st.session_state["access_token"] = None
        st.write("You have been logged out.")
        st.button("Back to Dashboard", on_click=set_page, args=["dashboard_page"])

# Custom CSS for Styling
def add_custom_css():
    st.markdown(
        """
        <style>
        /* Force white background */
        body {
            background-color: #ffffff !important;
        }

        /* Center the logo and text */
        .logo-container {
            text-align: center;
            margin-top: 50px;
        }
        
        /* Water Drop */
        .water-drop {
            width: 80px;
            height: 120px;
            display: inline-block;
            border: 3px solid #dc50e6;
            border-radius: 50% 50% 50% 50% / 70% 70% 35% 35%;
            background: #ffffff;
            margin-bottom: 10px;
        }

        /* PHASE Text */
        .logo-text {
            color: #dc50e6 !important;
            font-size: 36px;
            font-weight: bold;
            margin-top: -20px;
            text-decoration: none !important; /* Remove any link behavior */
        }

        /* Form Heading */
        .form-heading {
            color: #dc50e6 !important;
            font-size: 24px;
            text-align: center;
            margin-bottom: 30px;
        }

        /* Align buttons side-by-side and center them */
        .button-row {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
        }

        /* Button Styles */
        .stButton button {
            background-color: #dc50e6 !important;
            color: white !important;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            width: 120px; /* Ensures both buttons are of equal size */
        }
        .stButton button:hover {
            background-color: #bf3dbd !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    
def set_access_token_and_navigate(token, page):
    st.session_state["access_token"] = token
    st.session_state["page"] = page
    
# Helper to set success message and navigate to the next page
def set_success_and_navigate(success_message, next_page):
    st.session_state["success_message"] = success_message
    st.session_state["page"] = next_page
    
def login_page():
    add_custom_css()

    st.markdown(
        """
        <div class="logo-container">
            <div class="water-drop"></div>
            <div style="font-size: 36px; font-weight: bold; color: #dc50e6; text-align: center;">PHASE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="form-heading">Log In</div>', unsafe_allow_html=True)

    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")

    col1, col2, col3 = st.columns([1, 2, 1])  # Adjust column widths for placement
    with col1:
        st.write(" ")  # Empty for spacing
    with col2:
        login_button_col, signup_button_col = st.columns([1, 1], gap="large")
        with login_button_col:
            def handle_login():
                payload = {"email": login_email, "password": login_password}
                result = authenticate("login", payload)
                if result and "access_token" in result:
                    st.session_state["access_token"] = result["access_token"]
                    if fetch_cycle_data():  # Fetch and store cycle data
                        set_success_and_navigate("Login successful!", "main")
                    else:
                        st.error("Login successful, but failed to load your cycle data. Please update it on the dashboard.")
                else:
                    st.session_state["success_message"] = "Invalid credentials. Please try again."

            st.button("Log In", key="login_button", on_click=handle_login)

        with signup_button_col:
            st.button("Sign Up", key="signup_redirect_button", on_click=set_page, args=["signup"])
    with col3:
        st.write(" ")
        
    # Display success or error message
    if "success_message" in st.session_state:
        st.info(st.session_state.pop("success_message"))
        
# Sign Up Page
def signup_page():
    add_custom_css()

    st.markdown(
        """
        <div class="logo-container">
            <div class="water-drop"></div>
            <div style="font-size: 36px; font-weight: bold; color: #dc50e6; text-align: center;">PHASE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="form-heading">Sign Up</div>', unsafe_allow_html=True)

    # User details
    signup_email = st.text_input("Email", key="signup_email")
    signup_password = st.text_input("Password", type="password", key="signup_password")
    signup_name = st.text_input("Name", key="signup_name")
    signup_age = st.number_input("Age", min_value=10, max_value=100, step=1, key="signup_age")
    signup_height = st.number_input("Height (cm)", min_value=50, max_value=250, step=1, key="signup_height")
    signup_weight = st.number_input("Weight (kg)", min_value=20, max_value=200, step=1, key="signup_weight")

    # Cycle data
    signup_start_date = st.date_input("Period Start Date", key="signup_start_date")
    signup_end_date = st.date_input("Period End Date", key="signup_end_date")

    # Success message placeholder
    success_message = st.empty()

    col1, col2, col3 = st.columns([1, 2, 1])  # Adjust column widths for placement
    with col1:
        st.write("")  # Empty for spacing
    with col2:
        signup_button_col, back_to_login_col = st.columns([1, 1], gap="large")
        with signup_button_col:
            def handle_signup():
                payload = {
                    "email": signup_email,
                    "password": signup_password,
                    "name": signup_name,
                    "age": signup_age,
                    "height": signup_height,
                    "weight": signup_weight,
                }
                result = authenticate("signup", payload)
                if result and result.get("message") == "User created successfully":
                    login_payload = {"email": signup_email, "password": signup_password}
                    login_result = authenticate("login", login_payload)
                    if login_result and "access_token" in login_result:
                        st.session_state["access_token"] = login_result["access_token"]
                        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
                        cycle_payload = {
                            "period_start": signup_start_date.strftime("%Y-%m-%d"),
                            "period_end": signup_end_date.strftime("%Y-%m-%d"),
                        }
                        cycle_result = requests.post(f"{BASE_URL}/cycle-data", json=cycle_payload, headers=headers)
                        if cycle_result.status_code == 200 and fetch_cycle_data():
                            set_success_and_navigate("Sign-up successful! Redirecting to the main page...", "main")
                        else:
                            st.error("Sign-up successful, but failed to save cycle data. Please add it manually.")
                    else:
                        st.error("Sign-up successful, but login failed. Please log in manually.")
                else:
                    st.error("Sign-up failed. Please try again.")

            st.button("Sign Up", key="signup_button", on_click=handle_signup)

        with back_to_login_col:
            st.button("Log In", key="back_to_login_button", on_click=set_page, args=["login"])
    with col3:
        st.write("")  # Empty for spacing

        

def add_dashboard_css():
    st.markdown(
        """
        <style>
        body {
            background-color: #ffffff;  /* White background */
        }
        .water-drop {
            width: 80px;
            height: 120px;
            display: inline-block;
            border: 3px solid #dc50e6;
            border-radius: 50% 50% 50% 50% / 70% 70% 35% 35%;
            position: absolute;
            top: 2px;
            left: 10px;
            background: #ffffff;
            margin-bottom: 10px;
        }
        .welcome-text {
            font-family: 'Arial', sans-serif;
            color: #dc50e6;
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            margin-top: 80px;
        }

        .date-circle {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background-color: #dc50e6;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            cursor: pointer;
            margin: 20px auto;
        }

        .date-circle:hover {
            box-shadow: 0px 4px 15px rgba(220, 80, 230, 0.5);
        }

        .arrow-button {
            background: none;
            border: 2px solid #dc50e6;
            color: #dc50e6;
            font-size: 20px;
            border-radius: 50%;
            cursor: pointer;
            padding: 5px 10px;
            margin: 0 10px;
        }

        .phase-text {
            font-size: 24px;
            font-weight: bold;
            color: #dc50e6;
            text-align: center;
            margin-top: 20px;
        }

        .recommendations-section {
            margin-top: 20px;
        }

        .recommendations-header {
            font-size: 20px;
            font-weight: bold;
            color: #dc50e6;
            margin-bottom: 10px;
        }

        .recommendation-item {
            font-size: 16px;
            color: #333333;
            margin-bottom: 5px;
        }

        .exercise-header {
            font-size: 20px;
            font-weight: bold;
            color: #4caf50; /* Green color for exercise section */
            margin-top: 20px;
        }

        .notebook-icon {
            position: fixed;
            right: 20px;
            bottom: 20px;
            font-size: 32px;
            cursor: pointer;
            transition: transform 0.2s ease;
        }

        .notebook-icon:hover {
            transform: scale(1.2);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    
def run_select_date_function(selected_date):
    """Call the backend select-date function."""
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    payload = {
        "selected_date": selected_date.strftime("%Y-%m-%d"),
        "period_start": st.session_state.get("period_start"),
        "period_end": st.session_state.get("period_end"),
    }
    try:
        st.write("Payload being sent to the backend:", payload)  # Debugging log
        response = requests.post(
            f"{BASE_URL}/select-date",
            json=payload,
            headers=headers,
        )
        st.write("Backend response status:", response.status_code)  # Debugging log
        st.write("Backend response text:", response.text)  # Debugging log
        if response.status_code == 200:
            return response.json()  # Return the phase response
        else:
            st.error(response.json().get("error", "Failed to fetch phase."))
            return None
    except Exception as e:
        st.error(f"Error fetching phase: {e}")
        return None
    
def fetch_cycle_data():
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    try:
        response = requests.get(f"{BASE_URL}/cycle-data", headers=headers)
        if response.status_code == 200:
            cycle_data = response.json()
            st.session_state["period_start"] = datetime.strptime(cycle_data["period_start"], "%Y-%m-%d").date()
            st.session_state["period_end"] = datetime.strptime(cycle_data["period_end"], "%Y-%m-%d").date()
            return True
        else:
            st.warning("Failed to fetch cycle data. Please update your data.")
            return False
    except Exception as e:
        st.error(f"Error fetching cycle data: {e}")
        return False
    
def set_selected_date(delta_days):
    """Callback to update the selected date by delta days."""
    st.session_state.selected_date += timedelta(days=delta_days)

# Main page layout
def dashboard_page():
    # Apply custom CSS
    add_dashboard_css()

    # Ensure `selected_date` is initialized in session state
    if 'selected_date' not in st.session_state:
        st.session_state['selected_date'] = datetime.now().date()

    today = st.session_state.selected_date

    # Header Section
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="display: inline-block; border: 3px solid #dc50e6; background-color: #ffffff; width: 80px; height: 120px; border-radius: 50% 50% 50% 50% / 70% 70% 35% 35%;"></div>
            <div style="color: #dc50e6; font-size: 24px; font-weight: bold;">Welcome to PHASE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Arrow Button and Circle Layout
    col1, col2, col3 = st.columns([0.8, 2.8, 0.9], gap="small")

    with col1:
        st.button("◀", on_click=set_selected_date, args=[-1], key="prev_day")

    with col2:
        st.markdown(
            f"""
            <div style="
                display: flex; 
                justify-content: center; 
                align-items: center; 
                width: 150px; 
                height: 150px; 
                border-radius: 50%; 
                background-color: #dc50e6; 
                color: white; 
                font-size: 24px; 
                font-weight: bold; 
                margin: auto;">
                {today.strftime('%Y-%m-%d')}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.button("▶", on_click=set_selected_date, args=[1], key="next_day")

    # Fetch menstrual phase automatically
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    try:
        response = requests.post(
            f"{BASE_URL}/menstrual-phase",
            json={
                "period_start": st.session_state.get("period_start").strftime("%Y-%m-%d"),
                "period_end": st.session_state.get("period_end").strftime("%Y-%m-%d"),
            },
            headers=headers,
        )

        if response.status_code == 200:
            phase_data = response.json()
            current_phase = phase_data.get("phase", "Unknown")

            # Display phase and message
            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 20px;">
                    <h3 style="color: #dc50e6;">{('Predicted Phase: ' + phase_data['predicted_phase']) if current_phase == 'Prediction' else 'Current Phase: ' + current_phase}</h3>
                    <p style="font-size: 16px;">{phase_data.get('message', '')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Display recommendations
            food_recommendations = phase_data.get("food_recommendations", {})
            exercise_recommendations = phase_data.get("exercise_recommendations", {})
            lifestyle_tip = phase_data.get("lifestyle_tip", {})

            if food_recommendations:
                st.subheader("Food Recommendations")
                for category, details in food_recommendations.items():
                    st.markdown(
                        f"""
                        - **{category}**: {details.get('description', 'No description provided.')}
                        - **Food Sources**: {", ".join(details.get('food_sources', []))}
                        """
                    )

            if exercise_recommendations:
                st.subheader("Exercise Recommendations")
                st.markdown(
                    f"""
                    - **Description**: {exercise_recommendations.get('description', 'No description provided.')}
                    - **Activities**: {", ".join(exercise_recommendations.get('activities', []))}
                    """
                )

            if lifestyle_tip:
                st.subheader("Lifestyle Tips")
                for key, value in lifestyle_tip.items():
                    st.markdown(f"- **{key.capitalize()}**: {value}")

            if not food_recommendations and not exercise_recommendations and not lifestyle_tip:
                st.warning("No recommendations available for this phase.")
        else:
            st.error(response.json().get("error", "Failed to fetch phase details."))
    except Exception as e:
        st.error(f"Error retrieving phase details: {e}")

    # Log Out and Record Buttons in Columns
    col1, col2, col3 = st.columns([1, 2, 0.7], gap="large")

    with col1:
        st.button("Log Out", on_click=set_page, args=["logout"], key="logout_button")

    with col3:
        st.button("Record", on_click=set_page, args=["record_page"], key="record_button")
        
def update_phase_for_selected_date(selected_date):
    try:
        response = requests.post(
            f"{BASE_URL}/select-date",
            json={
                "period_start": st.session_state.get("period_start").strftime("%Y-%m-%d"),
                "period_end": st.session_state.get("period_end").strftime("%Y-%m-%d"),
                "selected_date": selected_date.strftime("%Y-%m-%d"),
            },
            headers={"Authorization": f"Bearer {st.session_state['access_token']}"},
        )

        if response.status_code == 200:
            result = response.json().get("phase", {})
            phase = result.get("phase", "Unknown")
            food_recommendations = result.get("food_recommendations", {})
            exercise_recommendations = result.get("exercise_recommendations", {})
            lifestyle_tip = result.get("lifestyle_tip", {})

            # Update the UI with the new phase and recommendations
            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 20px;">
                    <h3 style="color: #dc50e6;">Selected Phase: {phase}</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if food_recommendations:
                st.subheader("Food Recommendations")
                for category, details in food_recommendations.items():
                    st.markdown(
                        f"""
                        - **{category}**: {details.get('description', 'No description provided.')}
                        - **Food Sources**: {", ".join(details.get('food_sources', []))}
                        """
                    )

            if exercise_recommendations:
                st.subheader("Exercise Recommendations")
                st.markdown(
                    f"""
                    - **Description**: {exercise_recommendations.get('description', 'No description provided.')}
                    - **Activities**: {", ".join(exercise_recommendations.get('activities', []))}
                    """
                )

            if lifestyle_tip:
                st.subheader("Lifestyle Tips")
                for key, value in lifestyle_tip.items():
                    st.markdown(f"- **{key.capitalize()}**: {value}")

            if not food_recommendations and not exercise_recommendations and not lifestyle_tip:
                st.warning("No recommendations available for this phase.")

        else:
            st.error(response.json().get("error", "Failed to fetch phase for the selected date."))
    except Exception as e:
        st.error(f"Error fetching selected date phase: {e}")



def record_page():
    st.title("Record User Information")

    # User Input Fields
    age = st.number_input("Age", min_value=10, max_value=100, step=1)
    height = st.number_input("Height (cm)", min_value=50, max_value=250, step=1)
    weight = st.number_input("Weight (kg)", min_value=20, max_value=200, step=1)
    period_start = st.date_input("Period Start Date")
    period_end = st.date_input("Period End Date")

    # Buttons for Cancel and Save
    col1, col2, col3 = st.columns([1, 2, 0.7], gap="large")  
    with col1:
        # Navigate back to the previous page
        st.button("Cancel", on_click=set_page, args=[st.session_state.previous_page], key="cancel_button")
    with col3:
        # Save the record and navigate back to the previous page
        st.button("Save", on_click=save_record, args=[age, height, weight, period_start, period_end], key="save_button")


# Helper function to save data
def save_record(age, height, weight, period_start, period_end):
    notification_placeholder = st.empty()  # At the start of the function
    notification_placeholder.success("Information recorded successfully!")
    try:
        # Call the backend to save the record and get the updated phase information
        response = requests.post(
            f"{BASE_URL}/record",
            json={
                "age": age,
                "height": height,
                "weight": weight,
                "period_start": period_start.strftime("%Y-%m-%d"),
                "period_end": period_end.strftime("%Y-%m-%d"),
            },
            headers={"Authorization": f"Bearer {st.session_state['access_token']}"},
        )

        if response.status_code == 200:
            # Extract the updated recommendations and phase
            result = response.json()
            phase = result.get("phase", "Unknown")
            message = result.get("message", "")
            food_recommendations = result.get("food_recommendations", {})
            exercise_recommendations = result.get("exercise_recommendations", {})
            lifestyle_tip = result.get("lifestyle_tip", {})

            # Display updated phase and recommendations
            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 20px;">
                    <h3 style="color: #dc50e6;">Updated Phase: {phase}</h3>
                    <p style="font-size: 16px;">{message}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Display recommendations
            if food_recommendations:
                st.subheader("Food Recommendations")
                for category, details in food_recommendations.items():
                    st.markdown(
                        f"""
                        - **{category}**: {details.get('description', 'No description provided.')}
                        - **Food Sources**: {", ".join(details.get('food_sources', []))}
                        """
                    )

            if exercise_recommendations:
                st.subheader("Exercise Recommendations")
                st.markdown(
                    f"""
                    - **Description**: {exercise_recommendations.get('description', 'No description provided.')}
                    - **Activities**: {", ".join(exercise_recommendations.get('activities', []))}
                    """
                )

            if lifestyle_tip:
                st.subheader("Lifestyle Tips")
                for key, value in lifestyle_tip.items():
                    st.markdown(f"- **{key.capitalize()}**: {value}")

            if not food_recommendations and not exercise_recommendations and not lifestyle_tip:
                st.warning("No recommendations available for this phase.")

            # Set the page back to dashboard after showing success
            st.session_state.page = "dashboard_page"  # Explicitly set the page to dashboard
        else:
            # Handle any errors from the backend
            st.error(response.json().get("error", "Failed to record information."))
    except Exception as e:
        st.error(f"Error saving data: {e}")
        
    # Log Out and Record Buttons in Columns
    col1, col2, col3 = st.columns([1, 2, 0.7], gap="large")

    with col1:
        st.button("Log Out", on_click=set_page, args=["logout"], key="logout_button")

    with col3:
        st.button("Record", on_click=set_page, args=["record_page"], key="record_button")
        
def set_selected_date(offset):
    # Update the selected date in session state
    st.session_state.selected_date += timedelta(days=offset)

    # Call the backend to update phase and recommendations
    update_phase_for_selected_date(st.session_state.selected_date)
        

        
# Run the app
if __name__ == "__main__":
    main()