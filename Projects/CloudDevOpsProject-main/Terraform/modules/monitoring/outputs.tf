output "cloudwatch_dashboard_url" {
  value       = "https://${var.region}.console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards:name=${aws_cloudwatch_dashboard.jenkins_monitoring.dashboard_name}"
  description = "URL to the Jenkins monitoring CloudWatch dashboard"
}


output "sns_topic_arn" {
  value = aws_sns_topic.alerts.arn
}