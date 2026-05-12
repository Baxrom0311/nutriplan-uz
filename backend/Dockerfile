FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set working directory
WORKDIR /app

# Install python dependencies
COPY requirements/ /app/requirements/
RUN pip install --upgrade pip
RUN pip install -r requirements/production.txt

# Copy project files
COPY . /app/

# Expose port
EXPOSE 8000

# Run gunicorn inside the container
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
