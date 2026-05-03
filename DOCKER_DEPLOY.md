# Docker: build, run, and deploy

This project can be containerized to ensure the runtime in production matches your local environment.

Local build & run (no dockerhub):

```bash
# build the image
docker build -t sti-knowledge-dashboard:latest .

# run the container (port 8501 exposed)
docker run --rm -p 8501:8501 sti-knowledge-dashboard:latest
```

Local dev with docker-compose (live code via volume):

```bash
docker-compose up --build
# open http://localhost:8501
```

Push to Docker Hub (example):

```bash
# tag and push
docker tag sti-knowledge-dashboard:latest <your-dockerhub-username>/sti-knowledge-dashboard:latest
docker push <your-dockerhub-username>/sti-knowledge-dashboard:latest
```

Deploying the container image:

- Streamlit Community Cloud DOES NOT support custom Docker containers. If you use Streamlit Cloud you must rely on `requirements.txt` and the platform's build environment.
- Use a container-friendly host to run this image so the runtime matches local exactly. Options:
  - Render (Web Service) — supports Docker images from Docker Hub or GitHub Container Registry
  - Fly.io — deploy via `fly deploy` or by pushing image
  - Heroku Container Registry — `heroku container:push` and release
  - AWS ECS / Fargate, Azure App Service (Containers), Google Cloud Run

Example notes for Render (Docker Hub):
1. Push your image to Docker Hub (see above).
2. Create a new Web Service in Render and choose Docker image from Docker Hub.
3. Set the exposed port to `8501` if prompted and any environment variables you need.

Why this helps with color/appearance parity
- A Docker image packages the Python interpreter, libraries (Streamlit, Plotly, Pillow), and system libs in one immutable image — removing differences caused by different platform package versions.
- You can test the exact image locally and then run the same image in production.

Caveats
- If you must use Streamlit Cloud, Docker won't help; instead pin exact package versions (`pip freeze`) and include `.streamlit/config.toml` to lock theme settings. We've already added `Pillow` and `.streamlit/config.toml` in the repo.

If you want, I can:
- create and push an image to your Docker Hub (you must provide credentials or run the push locally),
- or prepare a Render deployment guide with exact steps for creating the service and env vars.
