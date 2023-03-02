FROM quay.io/ansible/awx-ee:21.12.0

COPY requiremens.txt /

RUN pip install --upgrade pip && \
    pip install --upgrade -r ./requirements.txt

RUN ansible-galaxy collection install git+https://github.com/kalenpeterson/ansible-orion.git
