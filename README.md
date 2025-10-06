# ======================= STEPS TO RUN THE PROJECT ==================================
# Step - 1.   
python -m venv venv


# Step - 2.   
venv\scripts\activate


# Step - 3.   
pip install -r requirements.txt



# Step - 4.   
alembic init -t async alembic

# Step - 5.   
alembic revision --autogenerate -m "create table"

# Step - 6.   
alembic upgrade head

# Step - 7.   
alembic stamp head



# Step - 8.   
fastapi dev app/main.py