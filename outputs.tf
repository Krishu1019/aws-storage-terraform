output "api_url" {
  value = aws_apigatewayv2_api.api.api_endpoint
}

output "ci_role_arn" {
  value = aws_iam_role.github_ci.arn
}
