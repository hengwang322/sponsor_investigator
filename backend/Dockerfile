FROM public.ecr.aws/lambda/python:3.9
RUN yum -y update; yum clean all
COPY requirements/prod.txt .
RUN pip install \
    --no-cache-dir \
    -r prod.txt
COPY model  ${LAMBDA_TASK_ROOT}/model
COPY src/runner.py  ${LAMBDA_TASK_ROOT}
COPY src/loader.py  ${LAMBDA_TASK_ROOT}
CMD [ "runner.handler" ]