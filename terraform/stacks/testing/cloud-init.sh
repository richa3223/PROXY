#cloud-config
hostname: ${hostname}
package_update: true
package_upgrade: true
packages:
  - software-properties-common
  - git
  - unzip
  - make
  - dnsutils
runcmd:
  - |
    # Install Python
    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install -y python3.9 python3.9-dev python3.9-distutils
    # Install pip
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3.9 get-pip.py
    python3.9 -m pip install --upgrade pip setuptools
    # Install cffi - required by poetry
    python3.9 -m pip install cffi
    # Install poetry
    python3.9 -m pip install poetry
    # Install AWS CLI
    wget "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -O "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    # Get Private Key
    aws secretsmanager get-secret-value --secret-id ${key_pair} --query SecretString --output text > /home/ubuntu/.ssh/gh.pem
    chmod 400 /home/ubuntu/.ssh/gh.pem
    chown ubuntu:ubuntu /home/ubuntu/.ssh/gh.pem
    # Configure ssh
    echo "Host github.com\n\tHostname github.com\n\tIdentityFile=/home/ubuntu/.ssh/gh.pem" > /home/ubuntu/.ssh/config
    sudo -i -u ubuntu ssh-keyscan github.com >> /home/ubuntu/.ssh/known_hosts
    # Get test scripts
    sudo -i -u ubuntu git clone git@github.com:NHSDigital/proxy-validated-relationships-service.git /home/ubuntu/proxy-validated-relationships-service
    # Install test script dependencies
    sudo -i -u ubuntu bash -c 'cd /home/ubuntu/proxy-validated-relationships-service/tests && poetry install'
    curl https://login.apigee.com/resources/scripts/sso-cli/ssocli-bundle.zip -o ssocli-bundle.zip
    unzip ssocli-bundle.zip -d /home/ubuntu/temp_install
    cd /home/ubuntu/temp_install && sudo ./install -b /usr/local/bin || exit
    cd - || exit
    rm -rf /home/ubuntu/temp_install
    echo 'export SSO_LOGIN_URL=https://login.apigee.com' > /home/ubuntu/.bash_profile
    echo 'export MASTER_HOST=master.main.internal' >> /home/ubuntu/.bash_profile
    echo 'export ENVIRONMENT=dev' >> /home/ubuntu/.bash_profile
    echo 'export APIGEE_ENVIRONMENT=internal-qa' >> /home/ubuntu/.bash_profile
    echo 'echo ${hostname} ready to run load testing' >> /home/ubuntu/.bash_profile
