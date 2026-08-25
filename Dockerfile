FROM python:3.11-slim

WORKDIR /app

# Zorg dat pip up-to-date is
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# De code wordt als package 'nis2app' gekopieerd (geen streepjes in de naam,
# want dat is geen geldige Python-module-naam). __init__.py maakt er een
# package van zodat de relatieve imports in app.py (from .database import ...)
# gewoon werken.
COPY __init__.py app.py database.py scanner.py questionnaire.py advies.py pdf_report.py ./nis2app/

EXPOSE 5077

ENV PORT=5077

CMD ["python", "-m", "flask", "--app", "nis2app.app", "run", "--host", "0.0.0.0", "--port", "5077"]
