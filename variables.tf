variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "bucket_name" {
  type    = string
  default = "storage-project-2026"
}

variable "api_key" {
  type      = string
  sensitive = true
}

variable "alert_email" {
  type = string
}
