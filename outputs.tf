output "sns_topic_arn" {
  value = data.aws_sns_topic.temperature_topic.arn
}

output "dynamodb_table_name" {
  value = data.aws_dynamodb_table.sensors.name
}