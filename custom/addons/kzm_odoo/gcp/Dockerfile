FROM registry.gitlab.com/odoo-kzm/gitlab_ci/odoo_images:odoo16_base

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8
ENV GIT_TERMINAL_PROMPT 1

ARG CI_COMMIT_BRANCH
ARG CI_PIPELINE_ID

ENV MY_BRANCH=$CI_COMMIT_BRANCH

ENV PIPE_ID=$CI_PIPELINE_ID


COPY ./odoo_deploy.conf /etc/odoo/odoo.conf

USER root

RUN rm -rf /mnt/extra-addons/OCA/server-tools
RUN mkdir -p /mnt/extra-addons/custom \
    && mkdir -p /mnt/extra-addons/custom/addons \
   && mkdir -p /mnt/extra-addons/custom/addons/kzm_odoo \
   && mkdir -p /mnt/extra-addons/OCA/partner-contact \
   && mkdir -p /mnt/extra-addons/OCA/server-tools

RUN git clone -b $MY_BRANCH https://oauth2:glpat-sFRRo-vs81qcSsEixubY@gitlab.com/odoo-kzm/projet-kzm/kzm_odoo.git /mnt/extra-addons/custom/addons/kzm_odoo  && \
    chown -R odoo:odoo /mnt/extra-addons/custom/addons/kzm_odoo

RUN git clone -b 16.0 https://github.com/OCA/partner-contact.git /mnt/extra-addons/OCA/partner-contact && \
    chown -R odoo:odoo /mnt/extra-addons/OCA/partner-contact

RUN git clone -b 15.0 https://github.com/OCA/server-tools.git /mnt/extra-addons/OCA/server-tools && \
    chown -R odoo:odoo /mnt/extra-addons/OCA/server-tools

RUN pip3 install odoo_test_helper && pip3 install fabric && pip3 install pydrive && pip3 install pysftp 
RUN pip3 install --upgrade google-cloud-storage


RUN pip3 install twilio
RUN pip3 install pandas
RUN pip install nexmo
RUN pip install cryptography==2.6.1
RUN pip install pyOpenSSL==19.0.0
#RUN pip3 install PyGitHub

EXPOSE 8069

CMD ["sh", "-c", "/usr/bin/odoo -c /etc/odoo/odoo.conf -d KZM-ODOO-$MY_BRANCH-$PIPE_ID -u base -i kzm_base"]


