<br />
<div align="center">
  <h3 align="center">Project</h3>
  <p align="center">
    Analyse images with carnet.ai or if Image doesn't contain a car with AWS Recognition.
    <br />
  </p>
</div>


<!-- ABOUT THE PROJECT -->
## Project Structure

<img src="images/structure.png" alt="project-1-aws" >
<!-- GETTING STARTED -->
## Getting Started

### Look for LabRole ARN and update the
`configuration.json`

### Install ServerLess framework

We need to install serverless framework.

  ```sh
  npm install serverless
  ```
### Check `credentials.json` key value pairs and set yours in repl __SECRETS__.

### Deploy your function
Move to `/rekognition` folder

```sh
cd ./carnet
```

Run
```sh
../node_modules/.bin/serverless deploy
```
