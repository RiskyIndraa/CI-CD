from flask import Flask, request, render_template, redirect, url_for, jsonify
import boto3
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# AWS Configuration (Using environment variables)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
API_URL = os.getenv("API_GATEWAY_URL")

if not API_URL:
    raise ValueError("❌ ERROR: API_GATEWAY_URL is not set! Please check your environment variables.")

# Initialize S3 Client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

@app.route("/")
def index():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        users = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch data from API: {str(e)}"}), 500

    return render_template("index.html", users=users, s3_bucket=f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/")

@app.route("/users", methods=["POST"])
def add_user():
    name = request.form.get("name")
    email = request.form.get("email")
    institution = request.form.get("institution")
    position = request.form.get("position")
    phone = request.form.get("phone")
    image = request.files.get("image")

    if not all([name, email, institution, position, phone]):
        return jsonify({"error": "All fields are required"}), 400

    image_url = ""
    if image:
        image_filename = f"users/{image.filename}"
        try:
            s3_client.upload_fileobj(image, S3_BUCKET, image_filename)
            image_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{image_filename}"
        except Exception as e:
            return jsonify({"error": f"Failed to upload image: {str(e)}"}), 500

    user_data = {
        "name": name,
        "email": email,
        "institution": institution,
        "position": position,
        "phone": phone,
        "image_url": image_url,
    }

    try:
        response = requests.post(API_URL, json=user_data, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to save user to RDS: {str(e)}"}), 500

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
