# Shared build definition for the PR workflows; select "app" for the published :base or "app-pr-base" for the PR's own base.
variable "IMAGE_TAG" {
  default = "kometa-ci:local"
}

variable "IMAGE_PLATFORMS" {
  default = "linux/amd64,linux/arm64"
}

variable "BRANCH_NAME" {
  default = "master"
}

variable "KOMETA_GIT_SHA" {
  default = ""
}

variable "KOMETA_VERSION" {
  default = ""
}

# No tags and no output of its own, so building it as a dependency never publishes it.
target "base" {
  context    = "."
  dockerfile = "docker/Dockerfile.base"
  platforms  = split(",", IMAGE_PLATFORMS)
}

target "app" {
  context    = "."
  dockerfile = "Dockerfile"
  platforms  = split(",", IMAGE_PLATFORMS)
  tags       = [IMAGE_TAG]
  args = {
    BRANCH_NAME    = BRANCH_NAME
    KOMETA_GIT_SHA = KOMETA_GIT_SHA
    KOMETA_VERSION = KOMETA_VERSION
  }
}

# The Dockerfile's FROM kometateam/kometa:base is replaced by the base built from this checkout.
target "app-pr-base" {
  inherits = ["app"]
  contexts = {
    "kometateam/kometa:base" = "target:base"
  }
}
