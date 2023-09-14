# Computer Vision Model Agnostic Application with containerized deployment managed by k8

### Usage Overview
The service can be accessed by sending a POST request to the inference service API, with a payload of an image to perform inference on, and a string with the specific inference task to perform. Options are: “classification,” “detection,” or “segmentation.” In the case of classification, the API response will be a label in the form of a string. For detection and segmentation, the API will return an image with a bounding box or a segmented image. 


### Running the pipeline
The two services are stored in two repositories: inference-service & preprocess-service.

1. Build each docker from their respective directories
```
Inference_service$ docker build -t infer-service:latest .
Preprocess_service$ docker build -t preprocess-service:latest .
```

2. Apply the deployment and service manifests for each service/app to the Minikube cluster:
* For the inference service/pod:
```
Inference_service $ kubectl apply -f infer_deployment.yaml
Inference_service $ kubectl apply -f infer_deployment.yaml
```

* For the inference service/pod:
```
Preprocess _service $ kubectl apply -f preprocess_deployment.yaml
Preprocess _service $ kubectl apply -f prepreocess_service.yaml
```
3. Add docker images to minikube cache:
```
minikube cache add inference-service:latest
minikube cache add preprocess-service:latest
```
4. Finally, to perform inference and run the pipeline end to end, enter the following command:
```
minikube service inference-service --url
```
This command will open a browser window and provide a URL that you can navigate to in order to access the FastAPI UI. 
Within the FastAPI UI, you can directly pass an image and a task to the pipeline to test it. 
