# Dockerfile
FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies
RUN yum install -y \
    pango \
    cairo \
    gobject-introspection \
    fontconfig \
    && yum clean all

# Copy your application code
COPY src/ ${LAMBDA_TASK_ROOT}/src/
COPY requirements.txt  ${LAMBDA_TASK_ROOT}/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# (Optional) expose a port if you are testing locally
# EXPOSE 8080

# Set the ENTRYPOINT (Handler)
CMD ["src.main.handler"]
