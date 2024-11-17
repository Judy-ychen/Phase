from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from models import db, User, CycleData

# Initialize Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret'

# Initialize Extensions
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


# Routes

# User Signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    user = User(
        email=data['email'],
        password=hashed_password,
        name=data['name'],
        age=data['age'],
        height=data['height'],
        weight=data['weight']
    )

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


# Add or Update Cycle Data
@app.route('/cycle-data', methods=['POST'])
@jwt_required()
def add_cycle_data():
    user_id = get_jwt_identity()
    data = request.json

    try:
        period_start = datetime.strptime(data['period_start'], '%Y-%m-%d').date()
        period_end = datetime.strptime(data['period_end'], '%Y-%m-%d').date()

        cycle_data = CycleData.query.filter_by(user_id=user_id).first()

        if cycle_data:
            # Update existing cycle data
            cycle_data.period_start = period_start
            cycle_data.period_end = period_end
        else:
            # Create new cycle data
            cycle_data = CycleData(user_id=user_id, period_start=period_start, period_end=period_end)
            db.session.add(cycle_data)

        db.session.commit()
        return jsonify({"message": "Cycle data saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get Cycle Data
@app.route('/cycle-data', methods=['GET'])
@jwt_required()
def get_cycle_data():
    user_id = get_jwt_identity()
    cycle_data = CycleData.query.filter_by(user_id=user_id).first()

    if cycle_data:
        return jsonify({
            "period_start": cycle_data.period_start.strftime('%Y-%m-%d'),
            "period_end": cycle_data.period_end.strftime('%Y-%m-%d')
        }), 200
    else:
        return jsonify({"message": "No cycle data found"}), 404
    
    
# Route: Get Menstrual Phase
@app.route('/menstrual-phase', methods=['POST'])
@jwt_required()
def get_menstrual_phase():
    user_id = get_jwt_identity()
    data = request.json

    # Inputs from request
    period_start = data['period_start']
    period_end = data['period_end']
    today_date = data.get('today_date', datetime.now().strftime('%Y-%m-%d'))

    # Try to determine the phase
    phase = determine_phase(period_start, period_end, today_date)

    if phase in recommendations:
        # If phase is determined, provide recommendations
        phase_data = recommendations[phase]
        response = {
            "phase": phase,
            "food_recommendations": phase_data.get("Food", {}),
            "exercise_recommendations": phase_data.get("Exercise", {}),
            "lifestyle_tip": phase_data.get("Lifestyle Tip", {})
        }
    else:
        # If determination fails, predict the phase
        response = predict_phase(user_id, today_date)

    return jsonify(response), 200

    

# Route: Record Data and Get Phase
@app.route('/record', methods=['POST'])
@jwt_required()
def record_user_data():
    user_id = get_jwt_identity()
    data = request.json

    try:
        # Update User Details
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        user.age = data.get('age', user.age)
        user.height = data.get('height', user.height)
        user.weight = data.get('weight', user.weight)

        # Update or Create Cycle Data
        period_start = datetime.strptime(data['period_start'], '%Y-%m-%d').date()
        period_end = datetime.strptime(data['period_end'], '%Y-%m-%d').date()

        cycle_data = CycleData.query.filter_by(user_id=user_id).first()
        if cycle_data:
            cycle_data.period_start = period_start
            cycle_data.period_end = period_end
        else:
            cycle_data = CycleData(user_id=user_id, period_start=period_start, period_end=period_end)
            db.session.add(cycle_data)

        db.session.commit()

        # Determine Menstrual Phase
        today_date = datetime.now().strftime('%Y-%m-%d')
        phase = determine_phase(period_start.strftime('%Y-%m-%d'), period_end.strftime('%Y-%m-%d'), today_date)

        # Validate phase in recommendations
        if phase in recommendations:
            phase_data = recommendations[phase]
            response = {
                "message": "User data and cycle records updated successfully.",
                "phase": phase,
                "food_recommendations": phase_data.get("Food", {}),
                "exercise_recommendations": phase_data.get("Exercise", {}),
                "lifestyle_tip": phase_data.get("Lifestyle Tip", {})
            }
        else:
            response = {
                "message": "User data updated successfully, but phase could not be determined.",
                "phase": "Unknown",
                "description": "Ensure the period start and end dates are valid."
            }

        return jsonify(response), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    
# Route: Predict Phase for Selected Date
@app.route('/select-date', methods=['POST'])
@jwt_required()
def select_date_phase():
    user_id = get_jwt_identity()
    data = request.json

    # Inputs from request
    period_start = datetime.strptime(data['period_start'], "%Y-%m-%d").date()
    period_end = datetime.strptime(data['period_end'], "%Y-%m-%d").date()
    selected_date = datetime.strptime(data['selected_date'], "%Y-%m-%d").date()
    today_date = datetime.now().date()

    # Determine the phase for today's date
    today_phase = determine_phase(period_start.strftime("%Y-%m-%d"),
                                  period_end.strftime("%Y-%m-%d"),
                                  today_date.strftime("%Y-%m-%d"))

    # If today's phase is determinable, proceed to calculate the selected date's phase
    if today_phase in recommendations:
        # Predict phase for the selected date
        cycle_length = 28  # Default cycle length
        menstrual_length = (period_end - period_start).days + 1
        follicular_length = 6
        ovulation_length = 5
        luteal_length = cycle_length - (menstrual_length + follicular_length + ovulation_length)

        days_since_start = (selected_date - period_start).days

        # Adjust to fit into a valid cycle
        if days_since_start < 0:
            full_cycles_back = (-days_since_start) // cycle_length + 1
            adjusted_start = period_start - timedelta(days=full_cycles_back * cycle_length)
            days_since_start = (selected_date - adjusted_start).days
        elif days_since_start >= cycle_length:
            full_cycles_forward = days_since_start // cycle_length
            adjusted_start = period_start + timedelta(days=full_cycles_forward * cycle_length)
            days_since_start = (selected_date - adjusted_start).days

        # Determine the phase within the cycle
        if 0 <= days_since_start < menstrual_length:
            predicted_phase = "Menstrual Phase"
        elif menstrual_length <= days_since_start < menstrual_length + follicular_length:
            predicted_phase = "Follicular Phase"
        elif menstrual_length + follicular_length <= days_since_start < menstrual_length + follicular_length + ovulation_length:
            predicted_phase = "Ovulation Phase"
        else:
            predicted_phase = "Luteal Phase"

        # Fetch recommendations for the predicted phase
        if predicted_phase in recommendations:
            phase_data = recommendations[predicted_phase]
            response = {
                "phase": {
                    "phase": predicted_phase,
                    "food_recommendations": phase_data.get("Food", {}),
                    "exercise_recommendations": phase_data.get("Exercise", {}),
                    "lifestyle_tip": phase_data.get("Lifestyle Tip", {})
                }
            }
        else:
            response = {
                "phase": {
                    "phase": predicted_phase,
                    "message": "We don't have detailed recommendations for this phase."
                }
            }
    else:
        # If today's phase cannot be determined, return an error
        response = {
            "error": "Cannot determine today's phase. Selected date phase cannot be predicted.",
            "phase": "Unknown"
        }

    return jsonify(response), 200
    

# Helper Function: Determine Phase
def determine_phase(period_start, period_end, today_date):
    period_start_date = datetime.strptime(period_start, "%Y-%m-%d")
    period_end_date = datetime.strptime(period_end, "%Y-%m-%d")
    today_date_obj = datetime.strptime(today_date, "%Y-%m-%d")

    follicular_start = period_end_date + timedelta(days=1)
    follicular_end = follicular_start + timedelta(days=6)

    ovulation_start = follicular_end + timedelta(days=1)
    ovulation_end = ovulation_start + timedelta(days=5)

    luteal_start = ovulation_end + timedelta(days=1)
    next_period_start = luteal_start + timedelta(days=13)

    if period_start_date <= today_date_obj <= period_end_date:
        phase = "Menstrual Phase"
    elif follicular_start <= today_date_obj <= follicular_end:
        phase = "Follicular Phase"
    elif ovulation_start <= today_date_obj <= ovulation_end:
        phase = "Ovulation Phase"
    elif luteal_start <= today_date_obj < next_period_start:
        phase = "Luteal Phase"
    else:
        phase = "Unknown Phase (possibly irregular cycle)"

    print(f"[DEBUG] Phase determined: {phase}")  # Debugging output
    return phase

def predict_phase(user_id, today_date):
    # Fetch user cycle data
    cycles = CycleData.query.filter_by(user_id=user_id).order_by(CycleData.period_start).all()
    if not cycles:
        return {
            "phase": "Unknown",
            "message": "We don't have enough data to make a prediction. Please update your cycle data."
        }

    last_cycle = cycles[-1]
    last_period_end = last_cycle.period_end
    average_cycle_length = calculate_average_cycle_length(user_id)

    # Predict the next cycle
    next_period_start = last_period_end + timedelta(days=average_cycle_length)
    next_period_end = next_period_start + timedelta(days=(last_cycle.period_end - last_cycle.period_start).days)

    # Prediction logic
    today_date_obj = datetime.strptime(today_date, "%Y-%m-%d")
    next_period_start_datetime = datetime.combine(next_period_start, datetime.min.time())

    if next_period_start_datetime - timedelta(days=7) <= today_date_obj <= next_period_start_datetime + timedelta(days=7):
        predicted_phase = "Follicular Phase"
        message = (
            f"In our prediction, you should be in the {predicted_phase}. "
            "Your cycle is slightly late but not unusual. Please update your data to help improve our predictions."
        )
    elif today_date_obj >= next_period_start_datetime + timedelta(days=30):
        predicted_phase = "Menstrual Phase"
        message = (
            f"In our prediction, you should be in the {predicted_phase}. "
            "Your cycle is significantly late, which may indicate a menstrual disorder. "
            "We recommend consulting a doctor. Here’s some advice to help regulate your body."
        )
    else:
        # Dynamically map today_date_obj into predicted phases
        days_from_start = (today_date_obj - next_period_start_datetime).days
        if 0 <= days_from_start <= 6:
            predicted_phase = "Follicular Phase"
        elif 7 <= days_from_start <= 12:
            predicted_phase = "Ovulation Phase"
        elif 13 <= days_from_start <= 27:
            predicted_phase = "Luteal Phase"
        else:
            predicted_phase = "Menstrual Phase"
        
        message = (
            f"In our prediction, you should be in the {predicted_phase}. "
            "Your cycle is late, but it's important to care for your health. "
            "Regulate your diet and mood."
        )

    return {
        "phase": "Prediction",
        "predicted_phase": predicted_phase,
        "message": message
    }

def calculate_average_cycle_length(user_id):
    cycles = CycleData.query.filter_by(user_id=user_id).order_by(CycleData.period_start).all()
    if len(cycles) < 2:
        return 28  # Default to 28 days if insufficient data
    lengths = [
        (cycles[i + 1].period_start - cycles[i].period_start).days
        for i in range(len(cycles) - 1)
    ]
    return sum(lengths) // len(lengths)



# Recommendations
recommendations = {
    "Menstrual Phase": {
        "Food": {
            "Iron-rich Foods": {
                "description": "To replenish iron lost during menstruation and prevent anemia.",
                "items": ["Leafy greens like spinach and kale", "Lean meats such as beef or turkey", "Legumes like lentils and chickpeas"]
            },
            "B Vitamin-rich Foods": {
                "description": "To support energy levels and mood.",
                "items": ["Whole grains like quinoa or whole wheat bread", "Eggs", "Dairy products like milk and cheese"]
            },
            "Omega-3 Fatty Acids": {
                "description": "To help with menstrual cramping and inflammation.",
                "items": ["Fatty fish like salmon or mackerel", "Nuts, especially walnuts", "Seeds like chia seeds and flaxseeds"]
            },
            "Magnesium-rich Foods": {
                "description": "To help with menstrual cramping and sleep.",
                "items": ["Dark chocolate", "Avocado", "Bananas"]
            },
            "Fiber-rich Foods": {
                "description": "To support digestive health.",
                "items": ["Whole grains", "Vegetables like broccoli and carrots", "Fruits like berries and apples"]
            }
        },
        "Exercise": {
            "description": "You have less energy, so this is the time for low-intensity activities, such as walking, stretching, or Pilates. You may not feel like exercising at all, and that’s OK.",
            "activities": ["Walking", "Stretching", "Pilates"]
        }
    },
    "Luteal Phase": {
        "Food": {
            "Healthy Fats & Vitamin B6": {
                "description": "These nutrients help support overall hormonal balance and healthy skin.",
                "food_sources": ["Avocado", "Wild salmon", "Walnuts"]
            },
            "Serotonin-Boosting Foods": {
                "description": "These foods help to improve mood by increasing serotonin levels in the body.",
                "food_sources": ["Quinoa", "Buckwheat"]
            },
            "Support for Progesterone Levels": {
                "description": "These foods help promote healthy progesterone levels, which support the luteal phase.",
                "food_sources": ["Sesame seeds", "Sunflower seeds"]
            },
            "Magnesium-Rich Foods": {
                "description": "Magnesium helps to regulate mood and prevent cramping.",
                "food_sources": ["Spinach", "Bananas", "Dark chocolate"]
            },
            "General Mood and Skin Health": {
                "description": "These foods help with overall mood and skin health during this phase.",
                "food_sources": ["Red meat", "Carrots", "Sweet potato", "Lentils", "Oats"]
            }
        },
        "Exercise": {
            "description": "Take advantage of your peak energy levels with high-intensity workouts",
            "activities": ["Kickboxing", "Cycling", "Sprints"]
        },
        "Lifestyle Tip": {
            "description": "Remember to reduce intake of caffeine, alcohol, added salt, and carbonated drinks to minimize stress on the liver during this phase."
        }
    },
    "Follicular Phase": {
        "Food": {
            "Hormonal Balance": {
                "description": "Supports overall hormonal balance and prepares the body for ovulation.",
                "food_sources": [
                    "Fresh vegetables (artichokes, broccoli, carrots, parsley, green peas, string beans, zucchini)",
                    "Fresh fruits (berries, citrus fruits, apples)",
                    "Lean proteins (poultry, fish, legumes, tofu)",
                    "Healthy fats (avocados, nuts, seeds, olive oil)"
                ]
            },
            "Energy Levels": {
                "description": "Boosts energy and supports daily activities.",
                "food_sources": [
                    "Whole grains (quinoa, brown rice, whole wheat)",
                    "Lean proteins (poultry, fish, legumes, tofu)"
                ]
            },
            "Digestive Health": {
                "description": "Supports a healthy gut and digestion.",
                "food_sources": [
                    "Fermented foods (kimchi, sauerkraut, kefir)",
                    "Fiber-rich foods (squash, green peas, sweet potatoes)",
                    "Sprouted grains and seeds"
                ]
            },
            "Iron": {
                "description": "Replenishes iron levels after menstruation.",
                "food_sources": [
                    "Lean meats",
                    "Plant-based sources (legumes, tofu)",
                    "Dark leafy greens",
                    "Fortified cereals"
                ]
            },
            "Zinc": {
                "description": "Supports immune function and cellular repair.",
                "food_sources": [
                    "Shellfish (oysters, crab)",
                    "Legumes (chickpeas, lentils)",
                    "Seeds (pumpkin, sesame)",
                    "Whole grains (quinoa, oats)"
                ]
            },
            "Vitamin D": {
                "description": "Promotes calcium absorption and supports bone health.",
                "food_sources": [
                    "Fatty fish (salmon, mackerel)",
                    "Fortified foods (milk, orange juice)",
                    "Egg yolks"
                ]
            }
        },
        "Exercise": {
            "description": "As your energy levels increase, start adding in cardio-based workouts.",
            "activities": ["Running", "Swimming", "Biking"]
        }
    },
    "Ovulation Phase": {
        "Food": {
            "Healthy Fats": {
                "description": "Supports hormone production and overall health.",
                "food_sources": ["Organic salmon", "Sardines", "Organic eggs", "Almonds"]
            },
            "Vitamin B6": {
                "description": "Essential for hormonal balance and neurotransmitter function.",
                "food_sources": ["Sunflower seeds", "Sesame seeds", "Organic red meat"]
            },
            "Folate": {
                "description": "Supports cellular repair and DNA synthesis.",
                "food_sources": [
                    "Leafy green vegetables (spinach, kale)",
                    "Peas",
                    "Kidney beans",
                    "High-quality folate supplement"
                ]
            },
            "Choline": {
                "description": "Supports brain function and liver health.",
                "food_sources": ["Organic eggs", "Seafood (oysters)"]
            },
            "Liver-Supporting Foods": {
                "description": "Supports detoxification and hormone metabolism.",
                "food_sources": ["Pumpkin", "Ginger"]
            },
            "Anti-Inflammatory Foods": {
                "description": "Reduces inflammation and supports overall health.",
                "food_sources": ["Berries", "Dark chocolate", "Garlic", "Vegetables", "Fatty fish"]
            }
        },
        "Exercise": {
            "description": "Take advantage of your peak energy levels with high-intensity workouts.",
            "activities": ["Kickboxing", "Cycling HIIT", "Sprints"]
        }
    }
}
    

# Initialize Database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='129.133.72.121', port=8080, debug=True)
