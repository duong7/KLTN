FROM jupyter/base-notebook:latest

USER root

# Cài đặt các thư viện bổ sung với các phiên bản cụ thể
RUN pip install pandas==2.0.1 numpy==1.23.5 matplotlib==3.7.1 seaborn==0.12.2 plotly==5.14.1 scikit-learn==1.2.2 streamlit==1.22.0

USER $NB_UID

FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run streamlit app when the container launches
CMD ["streamlit", "run", "Home.py"]
