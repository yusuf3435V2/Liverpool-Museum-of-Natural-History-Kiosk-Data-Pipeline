# Liverpool Museum of Natural History - Live Kiosk Data Pipeline

## Project Overview

This project implements a live ETL pipeline for the Liverpool Museum of Natural History kiosk data.

The pipeline consumes kiosk interaction messages from a Kafka topic, validates and transforms the messages, and inserts valid records into a PostgreSQL database hosted on AWS RDS.

The project also includes Terraform configuration to provision the required cloud infrastructure, including:

- AWS RDS PostgreSQL database
- AWS EC2 instance for hosting the pipeline
- Security groups
- SSH key configuration
- Outputs for connecting to cloud resources

A Tableau dashboard can then connect to the RDS database to visualise the live kiosk data.

---

## Project Structure

```text
dashboard/
├── Kafka_pipeline.py
├── reset_kiosk_interactions.sh
├── test_kafka_pipeline.py

deployment/
├── main.tf
├── outputs.tf
├── variables.tf

README.md
requirements.txt
schema.sql
.env
```
## Running The Project

### Cloning
Clone the repository using:
```
git clone https://github.com/yusuf3435V2/Liverpool-Museum-of-Natural-History-Kiosk-Data-Pipeline
cd Coursework-Advanced-Data-Week-1
```
### Installation
To install required packages run:
```bash 
pip install -r requirements.txt
```
### .env
Create a .env file in the root folder in this format:
```
DB_NAME=museum
DB_USER=museum_admin
DB_PASSWORD=your_database_password
DB_HOST=your_rds_endpoint
DB_PORT=5432

BOOTSTRAP_SERVERS=your_kafka_bootstrap_server
SECURITY_PROTOCOL=SASL_SSL
SASL_MECHANISM=PLAIN
USERNAME=your_kafka_username
PASSWORD=your_kafka_password
KAFKA_TOPIC=lmnh
KAFKA_GROUP_ID=1
```
### Configure AWS CLI
Make sure your AWS credentials are configured:
```
aws configure
```
### Create an SSH Key for EC2
Create an SSH key to log into the EC2, this can be done by doing this:
```
ssh-keygen -t ed25519 -f ~/.ssh/lmnh_ec2_key
```

