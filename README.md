
## Pre-requisites

- **Sanic** - Web server framework
- **Motor** - Async MongoDB driver for Python
- **zrok** - Tool for sharing private resources via tunneling (for MongoDB access)
- Any other required dependencies (e.g., `passlib`, `jwt`, etc.)

## Installation

1. To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

2. To install the checkpoints, run the following command:
```bash
bash checkpoints.sh
```
(If you are using wsl, dont open the `checkpoints.sh` file because it will cause some character errors in the file)

3. Add .env file in the root directory:
```env
MONGO_URI= 
DB_NAME=
SECRET_KEY=
```

## How to Use

1. Run the following command:
```bash
sanic app
```

## How to Use (deprecated)

1. **Install zrok**: If you haven't installed zrok yet, visit [zrok.io](https://zrok.io) to download and set it up.

2. **Enable zrok for Tunneling**: Use the following command to enable your zrok account (replace token if you have account):

    ```bash
    zrok enable utz8rO7v1kIw
    ```

3. **Expose MongoDB through zrok**:

    ```bash
    zrok access private c9z6hhgbbi08
    ```

    By default, zrok will expose MongoDB on port `9191`.

**Khang Nguyen Beo**
