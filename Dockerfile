FROM harbor.hpc.ford.com/python-coe/python-ub@sha256:edc0ad2254c0fc3fc0964e549fe220b3c2467316913aa4f71d53311c4152786c

USER root

RUN mkdir /files/

COPY . /files/modal-analysis

WORKDIR /files/modal-analysis

ENV HOME=/files/modal-analysis

# Install uv
RUN pip install uv

# Install dependencies using uv
RUN uv sync --frozen

RUN chmod 777 /files/ -R

USER python_user

# Only set PYTHONPATH to help with module imports
ENV PYTHONPATH=/files/modal-analysis

# Expose port 5000 for Flask
EXPOSE 5000

# Start the Flask application
CMD ["uv", "run", "python", "-m", "backend.app"]
