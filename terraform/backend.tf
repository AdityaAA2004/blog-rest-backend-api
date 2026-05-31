terraform {
  backend "gcs" {
    bucket = "blog-rest-backend-api-tf-state"
    prefix = "blog-rest-backend-api/terraform/state"
  }
}
