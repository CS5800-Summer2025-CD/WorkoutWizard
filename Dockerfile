# 1. Start with a Python base
FROM python:3.11-slim

# 2. Create a folder inside the container for your app
WORKDIR /app

# 3. Copy your specific requirements.txt into the container
COPY requirements.txt .

# 4. Install all the libraries from your requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your project (index.html, app.py, db.json) into the container
COPY . .

# 6. Open the "door" (port) so we can see the website
EXPOSE 8080

# 7. Start the server using Gunicorn (professional grade)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]