FROM python:3.13-slim
WORKDIR /src
COPY . .
RUN pip install --no-cache-dir -e . && pip install --no-cache-dir -r demo/api/requirements.txt
WORKDIR /src/demo/api
EXPOSE 5080
# Dev-only image (uvicorn --reload, not a production ASGI deployment) - mirrors
# tnzapi-dotnet's Api Dockerfile using `dotnet watch run` for the same purpose.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5080", "--reload"]
