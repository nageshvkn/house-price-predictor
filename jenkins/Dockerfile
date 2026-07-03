FROM jenkins/jenkins:lts-jdk17

USER root

# docker.io gives us the `docker` CLI so pipeline stages can build/run images
# against the host's Docker daemon via the mounted socket (Docker-outside-of-Docker).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       python3 python3-pip python3-venv \
       docker.io make git curl \
    && rm -rf /var/lib/apt/lists/* \
    && usermod -aG docker jenkins

# Skip the "getting started" plugin wizard prompts; keep the setup wizard
# itself so the facilitator can grab the initial admin password live.
RUN jenkins-plugin-cli --plugins git workflow-aggregator blueocean
