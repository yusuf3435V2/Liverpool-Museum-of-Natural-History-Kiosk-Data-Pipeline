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

### 1.Cloning
Clone the repository using:
```
git clone https://github.com/yusuf3435V2/Liverpool-Museum-of-Natural-History-Kiosk-Data-Pipeline
cd Coursework-Advanced-Data-Week-1
```
### 2.Installation
To install required packages run:
```bash 
pip install -r requirements.txt
```
### 3..env
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
### 4.Configure AWS CLI
Make sure your AWS credentials are configured:
```
aws configure
```
### 5.Create an SSH Key for EC2
Create an SSH key to log into the EC2, this can be done by doing this:
```
ssh-keygen -t ed25519 -f ~/.ssh/lmnh_ec2_key
```
### 6.Configure Terraform Variables
Go to the Terraform folder:
```
cd deployment
```
Create a terraform.tfvars file:
```
nano terraform.tfvars
```
Add values required by your Terraform configuration, for example:
```
my_ip          = "YOUR_PUBLIC_IP/32"
public_key_path = "~/.ssh/lmnh_ec2_key.pub"
db_password   = "your_database_password"
```
### 7.Initialise Terraform
From inside the deployment folder:
```
terraform init
9. Format and Validate Terraform
terraform fmt
terraform validate
10. Preview Infrastructure Changes
terraform plan
```
Check that Terraform plans to create the expected resources, such as:
```
RDS PostgreSQL database
EC2 instance
security groups
key pair
outputs
11. Apply Terraform
terraform apply
```
Type:
```
yes
```
Wait for the infrastructure to finish creating.

### 8.Get Terraform Outputs
Run:
```
terraform output
```
Record the values for:
```
RDS endpoint
EC2 public IP
EC2 public DNS
```
### 9.Update the .env File with the RDS Endpoint
Return to the project root:
```
cd ..
nano .env
```
Update:
```
DB_HOST=your_actual_rds_endpoint
```
Save and exit.

### 10.Create the Database Schema
From the project root, run:
```
psql "host=<RDS_ENDPOINT> port=5432 dbname=museum user=<DB_USER> sslmode=require" -f schema.sql
```
Enter the database password when prompted.
This creates the required database tables.

### 11.Check the Tables Were Created
Connect to the database:
```
psql "host=<RDS_ENDPOINT> port=5432 dbname=museum user=<DB_USER> sslmode=require"
```
Then run:
```
\dt
```
You should see tables such as:
```
exhibition
kiosk_interaction
```
### 12.Test the Pipeline Locally
Run:
```
python3 dashboard/Kafka_pipeline.py
```
The script should:
```
connect to Kafka
consume messages from the lmnh topic
validate messages
transform valid records
insert records into RDS
```
Stop it with:
```
Ctrl + C
```
### 13.Verify Data Was Inserted
Connect to PostgreSQL:
```
psql "host=<RDS_ENDPOINT> port=5432 dbname=museum user=<DB_USER> sslmode=require"
```
Check the latest rows:
```
SELECT *
FROM kiosk_interaction
ORDER BY at DESC
LIMIT 5;
```
Check total rows:
```
SELECT COUNT(*)
FROM kiosk_interaction;
```
### 14.SSH into the EC2 Instance
Use the EC2 public IP from Terraform output:
```
ssh -i ~/.ssh/lmnh_ec2_key ubuntu@<EC2_PUBLIC_IP>
```
### 15.Install Required System Packages on EC2
On EC2, run:
```
sudo apt update
sudo apt install -y python3 python3-pip git postgresql-client
```
Check versions:
```
python3 --version
pip3 --version
psql --version
```
### 16.Clone the Repository on EC2
On EC2:
```
git clone https://github.com/yusuf3435V2/Liverpool-Museum-of-Natural-History-Kiosk-Data-Pipeline
cd Coursework-Advanced-Data-Week-1
```
### 17. Install Python Dependencies on EC2
```
pip3 install -r requirements.txt
```
### 18.Create the .env File on EC2
On EC2, inside the project root:
```
nano .env
```
Paste in your local .env

### 19.Run the Pipeline on EC2 in the Foreground First
Run:
```
python3 dashboard/Kafka_pipeline.py
```
Check that it logs messages and inserts data into the database.

### 20.Run the Pipeline in the Background on EC2
Run:
```
nohup python3 dashboard/Kafka_pipeline.py > kafka_pipeline.log 2>&1 &
```
### 21.View Pipeline Logs
Run:
```
tail -f kafka_pipeline.log
```
You should see logs showing the pipeline consuming, validating, transforming, and inserting messages.

### 22.Stop the Background Pipeline
Find the process ID:
```
pgrep -f Kafka_pipeline.py
```
Stop it:
```
kill <PID>
```
Example:
```
kill 1234
```
### 23.Reset Kiosk Interaction Data
The reset script removes interaction rows but preserves tables and exhibition data.
Make the script executable:
```
chmod +x dashboard/reset_kiosk_interactions.sh
```
Run:
```
./dashboard/reset_kiosk_interactions.sh
```
The script should reset:
```
kiosk_interaction
```
but preserve:
```
exhibition
```
