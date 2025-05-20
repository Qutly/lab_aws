terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }

  backend "s3" {
    bucket                = "niezlybuckecik"
    key                     = "terraform.tfstate"
    region                = "us-east-1"
    encrypt               = true
    use_lockfile = true
  }
}

provider "aws" {
  region                  = "us-east-1"
  shared_credentials_files = ["~/.aws/credentials"]  
}

provider "archive" {}

data "aws_iam_role" "main_role" {
  name = "LabRole"
}

data "aws_dynamodb_table" "sensors" {
  name = "sensors"
}

data "aws_sns_topic" "temperature_topic" {
  name = "sns_sensor_temperature"
}

resource "aws_lambda_function" "sensor_lambda" {
  filename         = "${path.module}/lambda_payload.zip"
  function_name    = "sensorHandler"
  role             = data.aws_iam_role.main_role.arn  # użycie istniejącej roli
  handler          = "sensor_handler.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("${path.module}/lambda_payload.zip")
  timeout          = 10

  environment {
    variables = {
      SNS_TOPIC_ARN  = data.aws_sns_topic.temperature_topic.arn
      DYNAMODB_TABLE = data.aws_dynamodb_table.sensors.name
    }
  }
}