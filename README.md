# paddleocr


docker run --name invoice -p 9845:9845 -it -v $PWD:/paddle paddlepaddle/paddle:3.0.0b1 /bin/bash
apt-get install -y libzbar0
pip install pyzbar Pillow paddleocr fastapi uvicorn python-multipart

uvicorn src.api:app --reload --host 0.0.0.0 --port 9845
