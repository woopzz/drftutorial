output "ec2_main_public_ip" {
    value = aws_instance.main.public_ip
}

output "ec2_elasticsearch_public_ip" {
    value = aws_instance.elasticsearch.public_ip
}

output "ec2_elasticsearch_private_ip" {
    value = aws_instance.elasticsearch.private_ip
}

output "postgres_endpoint" {
    value = aws_db_instance.postgres.endpoint
}
