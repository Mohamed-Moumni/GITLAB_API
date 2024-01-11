FROM registry.gitlab.com/odoo-kzm/gitlab_ci/odoo_images:odoo16_base

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8
ENV GIT_TERMINAL_PROMPT 1

ARG CI_COMMIT_BRANCH
ARG ODOO_VS=16.0
ARG CI_PIPELINE_ID

ENV MY_BRANCH=$CI_COMMIT_BRANCH

ENV PIPE_ID=$CI_PIPELINE_ID
ENV MY_BRANCH=$CI_COMMIT_BRANCH

COPY ./odoo_deploy.conf /etc/odoo/odoo.conf
USER root


RUN mkdir -p /mnt/extra-addons/custom \
    && mkdir -p /mnt/extra-addons/custom/addons/kzm_project_tools \
   && mkdir -p /mnt/extra-addons/custom/kzm_hr \
   && mkdir -p /mnt/extra-addons/OCA/hr \
   && mkdir -p /mnt/extra-addons/OCA/website \
   && mkdir -p /mnt/extra-addons/custom/kzm_odoo 

RUN git clone -b $MY_BRANCH https://oauth2:glpat-sFRRo-vs81qcSsEixubY@gitlab.com/odoo-kzm/projet-kzm/kzm_project_tools.git /mnt/extra-addons/custom/addons/kzm_project_tools  && \
    chown -R odoo:odoo /mnt/extra-addons/custom/addons/kzm_project_tools


RUN git clone -b $ODOO_VS https://oauth2:glpat-sFRRo-vs81qcSsEixubY@gitlab.com/odoo-kzm/projet-kzm/kzm_odoo.git /mnt/extra-addons/custom/kzm_odoo  && \
    chown -R odoo:odoo /mnt/extra-addons/custom/kzm_odoo

RUN git clone -b $ODOO_VS https://oauth2:glpat-sFRRo-vs81qcSsEixubY@gitlab.com/odoo-kzm/projet-kzm/kzm_hr.git /mnt/extra-addons/custom/kzm_hr  && \
    chown -R odoo:odoo /mnt/extra-addons/custom/kzm_hr


RUN git clone -b $ODOO_VS https://github.com/OCA/hr.git /mnt/extra-addons/OCA/hr && \
    chown -R odoo:odoo /mnt/extra-addons/OCA/hr

RUN git clone -b $ODOO_VS https://github.com/OCA/website.git /mnt/extra-addons/OCA/website && \
    chown -R odoo:odoo /mnt/extra-addons/OCA/website



RUN pip3 install odoo_test_helper && pip3 install openai && pip3 install paramiko && pip3 install fabric2
RUN pip3 install --upgrade google-cloud-storage 
RUN pip3 install pysftp && pip3 install pandas
 

EXPOSE 8069

CMD ["sh", "-c", "/usr/bin/odoo -c /etc/odoo/odoo.conf -d KZM-PROJECT-TOOLS-$MY_BRANCH-$PIPE_ID -u base -i kzm_project_base"]




