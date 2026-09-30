terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-2" 
}

resource "aws_s3_bucket" "packages" {
  bucket = "simple-package-managerbucket" 
  tags = {
    Name        = "Bucket for package blobs"
    Environment = "Dev"
  }
}
