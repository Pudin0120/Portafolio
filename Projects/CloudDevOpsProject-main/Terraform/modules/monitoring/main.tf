data "aws_autoscaling_groups" "eks_node_asg" {
  filter {
    name   = "tag:eks:nodegroup-name"
    values = [var.node_group_name]
  }
}

data "aws_instances" "eks_nodes" {
  filter {
    name   = "tag:eks:nodegroup-name"
    values = [var.node_group_name]
  }
}

resource "aws_sns_topic" "alerts" {
  name = "cloudwatch-alerts-topic"
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.sns_email
}

resource "aws_cloudwatch_dashboard" "jenkins_monitoring" {
  dashboard_name = "jenkins-dashboard"
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric",
        x = 0, y = 0, width = 12, height = 6,
        properties = {
          metrics = [[ "AWS/EC2", "CPUUtilization", "InstanceId", var.jenkins_master_id ]],
          period  = 300,
          stat    = "Average",
          region  = var.region,
          title   = "Jenkins Master CPU"
        }
      },
      {
        type = "metric",
        x = 12, y = 0, width = 12, height = 6,
        properties = {
          metrics = [[ "AWS/EC2", "CPUUtilization", "InstanceId", var.jenkins_worker_id ]],
          period  = 300,
          stat    = "Average",
          region  = var.region,
          title   = "Jenkins Worker CPU"
        }
      },
      {
        type = "metric",
        x = 0, y = 6, width = 24, height = 6,
        properties = {
          metrics = [
                      for instance_id in data.aws_instances.eks_nodes.ids :
                      [ "AWS/EC2", "CPUUtilization", "InstanceId", instance_id ]

          ],
          period  = 300,
          stat    = "Average",
          region  = var.region,
          title   = "EKS NodeGroup CPU"
        }
      }
    ]
  })
}

resource "aws_cloudwatch_metric_alarm" "cpu_high_master" {
  alarm_name          = "HighCPU-JenkinsMaster"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "CPU > 80% on Jenkins Master"
  dimensions = {
    InstanceId = var.jenkins_master_id
  }
  alarm_actions = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "cpu_high_worker" {
  alarm_name          = "HighCPU-JenkinsWorker"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "CPU > 80% on Jenkins Worker"
  dimensions = {
    InstanceId = var.jenkins_worker_id
  }
  alarm_actions = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "node_group_avg_cpu" {
  alarm_name          = "EKSNodeGroup-HighCPU"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 120
  statistic           = "Average"
  threshold           = 70
  alarm_description   = "High CPU across EKS Node Group"
  dimensions = {
    AutoScalingGroupName = data.aws_autoscaling_groups.eks_node_asg.names[0]
  }
  alarm_actions = [aws_sns_topic.alerts.arn]
}
