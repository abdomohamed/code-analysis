    #!/bin/bash
    pip3 install --user -r requirements.txt
    mkdir -p ./repos
    cd repos

    if [ ! -d "aws-java-sample" ]; then
        echo "Cloning sample repo..."
        git clone https://github.com/aws-samples/aws-java-sample.git
    else
        echo "Directory aws-java-sample already exists. Skipping clone."
    fi

    sudo cp -r /root/.ssh/  ~/