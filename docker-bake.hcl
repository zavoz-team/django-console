variable "TAG" {
  default = "latest"
}

group "default" {
  targets = ["app"]
}

target "app" {
  dockerfile = "Dockerfile"
  target     = "run"
  platforms  = ["linux/amd64", "linux/arm64"]
  tags = [
    "gglamer/django-console:latest",
    "gglamer/django-console:${TAG}",
  ]
  output = ["type=registry"]
}
