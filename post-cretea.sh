	#!/bin/bash
	pip3 install --user -r requirements.txt
    mkdir -p ./repos
    cd repos
    
    echo "Cloning sample repo..."
    git clone https://github.com/aws-samples/aws-java-sample.git