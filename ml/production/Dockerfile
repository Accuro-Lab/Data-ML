FROM python:3.7
RUN pip install torch==1.7.0+cpu torchvision==0.8.1+cpu torchaudio==0.7.0 -f https://download.pytorch.org/whl/torch_stable.html fastapi uvicorn numpy pandas farm-haystack
EXPOSE 80
COPY ./app /app
COPY ./data /data
CMD ['export', "MKL_SERVICE_FORCE_INTEL=1"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]


ssh -i "accuroServer.pem" ubuntu@