variable "db_password" {
  description = "Master password for the RDS"
  type        = string
  sensitive   = true
}

variable "my_ip" {
  description = "IP address for SSH access"
  type        = string
}

variable "public_key_path" {
  description = "Path to the SSH key for EC2 access"
  type        = string
}