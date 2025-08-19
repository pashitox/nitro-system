
Ejemplo básico `main.tf`:

```hcl
provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "app_server" {
  ami           = "ami-0c55b159cbfafe1f0" # Amazon Linux 2
  instance_type = "t3.micro"

  tags = {
    Name = "proyecto-nitro"
  }
}
