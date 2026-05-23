# Use a lightweight Python base image based on Alpine Linux
FROM python:3.12-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the dependency file to the working directory
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application files to the container
COPY . .

# Expose port 5000 so the app is accessible from outside the container
EXPOSE 5000

# Define the default command to run the Flask app
CMD ["python", "app.py"]
