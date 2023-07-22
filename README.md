# Design and Development of User Identification System Based on Face Biometric Parameters Recognition.

The task of facial recognition is to automatically verify an individual's identity by analyzing and comparing their facial features to an existing database of faces.

A user identification system was created based on the recognition of facial biometric parameters, which was implemented in the website designed during the final work.
The web system consists of:
* registration page,
* login page,
* admin section,
* user section,
* facial recognition system as an additional layer of security.

During the final work, the traditional forms of face identification - `Eigenfaces` method, `Fisherfaces` method, and `LBP` method, neural networks, face identification methods using neural networks, programming languages and their respective libraries to design the given system were also investigated.

To create the system, the `Python` programming language and the relevant language libraries were used to create the website (`Flask`), store data (`SQLite`), and work with neural networks (`PyTorch`).
`OSNet` was chosen as a face recognition model, which was retrained with the face pictures of users registered on the website. The developed system also has the possibility to be integrated with other systems through the `API`.

## Installation

```bash
  cd model_training/deep-person-reid/
  
  # create environment
  conda create --name face-rec python=3.7 -y
  conda activate face-rec

  # install dependencies for the face recognition
  pip install -r requirements.txt

  # install torch and torchvision (select the proper cuda version to suit your machine)
  conda install pytorch torchvision cudatoolkit=9.0 -c pytorch -y

  # install face recognition model
  python setup.py develop
  
  # install dependecies for the website
  cd ../../
  pip install -r requirements.txt
```

## Run the project

```bash
  python app.py 
```