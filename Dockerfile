# 
FROM python:3.11

# Install from requirements.txt
COPY requirements.txt .

RUN pip install -r requirements.txt

# Prisma
RUN prisma generate

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8083"]
