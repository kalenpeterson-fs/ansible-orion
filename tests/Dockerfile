FROM registry.redhat.io/ansible-automation-platform-21/ee-supported-rhel8:latest

COPY requirements.txt ./

RUN pip install --upgrade pip && \
    pip install --upgrade -r ./requirements.txt

RUN ansible-galaxy collection install git+https://github.com/kalenpeterson/ansible-orion.git
