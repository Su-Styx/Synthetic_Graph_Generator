# Dockerfile
FROM rocker/r-ver:4.4.2

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# System libraries needed by Python scientific packages and R packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libxml2-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    libfontconfig1-dev \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libpng-dev \
    libtiff5-dev \
    libjpeg-dev \
    zlib1g-dev \
    libglpk-dev \
    libgmp-dev \
    libmpfr-dev \
    libgit2-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/docker.txt /app/requirements/docker.txt

# NOTE FOR FINAL DEPLOY: NO CACHE
# RUN python3 -m pip install --break-system-packages \
#     --no-cache-dir -r /app/requirements/docker.txt

RUN python3 -m pip install --break-system-packages \
    -r /app/requirements/docker.txt

# Install R packages required by ERGM_fit_runner.R.
RUN R -e "install.packages(c('network', 'ergm', 'sna', 'statnet.common','jsonlite'), repos='https://cloud.r-project.org')"

COPY . /app

RUN mkdir -p \
    /app/media \
    /app/media/ergm_uploads \
    /app/staticfiles

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]