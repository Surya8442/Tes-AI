import os

def run_container(name, image, port):

    command = f"docker run -d -p {port}:80 --name {name} {image}"

    result = os.popen(command).read()

    if result:
        return result
    else:
        return "Container Started Successfully"