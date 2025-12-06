from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# ---------------------------
# Allowed Units and Conversions
# ---------------------------

allowed_units = {
    "miles", "kilometers",
    "pounds", "kilograms",
    "celsius", "fahrenheit"
}


def convert_units(value, from_unit, to_unit):
    """
    Performs the actual unit conversion based on from_unit and to_unit.
    Returns the converted value or None if conversion is not supported.
    """
    # Length conversions
    if from_unit == "miles" and to_unit == "kilometers":
        return value * 1.60934
    if from_unit == "kilometers" and to_unit == "miles":
        return value / 1.60934

    # Weight conversions
    if from_unit == "pounds" and to_unit == "kilograms":
        return value * 0.453592
    if from_unit == "kilograms" and to_unit == "pounds":
        return value / 0.453592

    # Temperature conversions
    if from_unit == "celsius" and to_unit == "fahrenheit":
        return (value * 9/5) + 32
    if from_unit == "fahrenheit" and to_unit == "celsius":
        return (value - 32) * 5/9

    return None  # unsupported conversion


# ---------------------------
# /convert Endpoint
# ---------------------------

@app.route("/convert", methods=["POST"])
def convert():
    """
    Main conversion endpoint that handles all unit conversions.
    Validates input and returns converted result.
    """
    # Check if request contains JSON
    if not request.is_json:
        return jsonify({"error": "Input must be JSON"}), 400

    data = request.get_json()

    # Validate required fields
    required_fields = ["value", "from_unit", "to_unit"]
    for f in required_fields:
        if f not in data:
            return jsonify({"error": f"Missing field: {f}"}), 400

    value = data["value"]
    from_unit = str(data["from_unit"]).lower()
    to_unit = str(data["to_unit"]).lower()

    # Validate that value is a number
    try:
        value = float(value)
    except:
        return jsonify({"error": "Value must be a number"}), 400

    # Validate units exist in allowed list
    if from_unit not in allowed_units:
        return jsonify({"error": f"Unsupported from_unit: {from_unit}"}), 400

    if to_unit not in allowed_units:
        return jsonify({"error": f"Unsupported to_unit: {to_unit}"}), 400

    # Define unit categories
    category_pairs = {
        "miles": "length", "kilometers": "length",
        "pounds": "weight", "kilograms": "weight",
        "celsius": "temp", "fahrenheit": "temp"
    }

    # Prevent mixing categories (e.g., kg → Celsius)
    if category_pairs[from_unit] != category_pairs[to_unit]:
        return jsonify({
            "error": f"Cannot convert {from_unit} to {to_unit}. "
                     f"Units must be from the same category (length, weight, or temperature)."
        }), 400

    # Check for negative values in length and weight (optional validation)
    if value < 0 and category_pairs[from_unit] in ["length", "weight"]:
        return jsonify({
            "error": f"Negative values are not allowed for {category_pairs[from_unit]} conversions"
        }), 400

    # Perform conversion
    result = convert_units(value, from_unit, to_unit)
    if result is None:
        return jsonify({"error": "Conversion not supported"}), 400

    # Return successful response
    return jsonify({
        "input": {
            "value": data["value"],
            "from_unit": data["from_unit"],
            "to_unit": data["to_unit"]
        },
        "result": round(result, 4)  # Round to 4 decimal places for cleaner output
    }), 200


# ---------------------------
# /help Endpoint
# ---------------------------

@app.route("/help", methods=["GET"])
def help():
    """
    Help endpoint that explains how to use the API.
    Returns documentation in JSON format.
    """
    info = {
        "description": "Unit Converter API that supports length, weight, and temperature conversions.",
        
        "how_to_use": {
            "endpoint": "/convert",
            "method": "POST",
            "content_type": "application/json",
            "required_fields": ["value", "from_unit", "to_unit"]
        },
        
        "allowed_units": sorted(list(allowed_units)),
        
        "supported_conversions": [
            "miles ↔ kilometers",
            "pounds ↔ kilograms",
            "celsius ↔ fahrenheit"
        ],
        
        "example_requests": [
            {
                "description": "Convert miles to kilometers",
                "input": {
                    "value": 5,
                    "from_unit": "miles",
                    "to_unit": "kilometers"
                },
                "expected_output": {
                    "input": {"value": 5, "from_unit": "miles", "to_unit": "kilometers"},
                    "result": 8.0467
                }
            },
            {
                "description": "Convert celsius to fahrenheit",
                "input": {
                    "value": 0,
                    "from_unit": "celsius",
                    "to_unit": "fahrenheit"
                },
                "expected_output": {
                    "input": {"value": 0, "from_unit": "celsius", "to_unit": "fahrenheit"},
                    "result": 32.0
                }
            },
            {
                "description": "Convert pounds to kilograms",
                "input": {
                    "value": 150,
                    "from_unit": "pounds",
                    "to_unit": "kilograms"
                },
                "expected_output": {
                    "input": {"value": 150, "from_unit": "pounds", "to_unit": "kilograms"},
                    "result": 68.0388
                }
            }
        ],
        
        "validation_rules": {
            "negative_values": "Allowed for temperature only. Length and weight must be positive.",
            "unit_format": "Units are case-insensitive (Miles, miles, MILES all work)",
            "category_matching": "Cannot mix categories (e.g., cannot convert kg to celsius)"
        },
        
        "error_scenarios": [
            {
                "case": "Missing field",
                "example": {"value": 10, "from_unit": "miles"},
                "error": "Missing field: to_unit"
            },
            {
                "case": "Invalid unit",
                "example": {"value": 10, "from_unit": "meter", "to_unit": "miles"},
                "error": "Unsupported from_unit: meter"
            },
            {
                "case": "Category mismatch",
                "example": {"value": 50, "from_unit": "kilograms", "to_unit": "celsius"},
                "error": "Cannot convert kilograms to celsius"
            },
            {
                "case": "Non-numeric value",
                "example": {"value": "hello", "from_unit": "celsius", "to_unit": "fahrenheit"},
                "error": "Value must be a number"
            },
            {
                "case": "Negative length/weight",
                "example": {"value": -5, "from_unit": "miles", "to_unit": "kilometers"},
                "error": "Negative values are not allowed for length conversions"
            }
        ]
    }

    return jsonify(info), 200


# ---------------------------
# Root Endpoint (Optional)
# ---------------------------

@app.route("/", methods=["GET"])
def root():
    """
    Root endpoint that redirects users to /help
    """
    return jsonify({
        "message": "Welcome to Unit Converter API",
        "help": "Visit /help for documentation"
    }), 200


# ---------------------------
# Run Server
# ---------------------------

if __name__ == "__main__":
    # For local testing
    app.run(host="0.0.0.0", port=5000, debug=True)