output "db_endpoint" {
  description = "RDS endpoint for connecting to the PostgreSQL database"
  value       = aws_db_instance.museum_db.address
}

output "db_port" {
  description = "Port for the RDS PostgreSQL database"
  value       = aws_db_instance.museum_db.port
}

output "db_name" {
  description = "Initial database name"
  value       = aws_db_instance.museum_db.db_name
}

output "db_username" {
  description = "Master username for the RDS database"
  value       = aws_db_instance.museum_db.username
}

output "ec2_public_ip" {
  description = "Public IP address of the ETL EC2 instance"
  value       = aws_instance.etl_server.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS name of the ETL EC2 instance"
  value       = aws_instance.etl_server.public_dns
}