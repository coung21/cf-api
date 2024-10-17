
## Prerequisites

- **Sanic** - Web server framework
- **Motor** - Async MongoDB driver for Python
- **zrok** - Tool for sharing private resources via tunneling (for MongoDB access)
- Any other required dependencies (e.g., `passlib`, `jwt`, etc.)

## Installation

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## How to Use

1. **Install zrok**: If you haven't installed zrok yet, visit [zrok.io](https://zrok.io) to download and set it up.

2. **Enable zrok for Tunneling**: Use the following command to enable your zrok account (replace with your token):

    ```bash
    zrok enable utz8rO7v1kIw
    ```

3. **Expose MongoDB through zrok**: Run the following command to share your MongoDB instance (replace with your own private token):

    ```bash
    zrok access private 9h1syz522r2f
    ```

    By default, zrok will expose MongoDB on port `9191`.

Now your MongoDB instance is accessible through the shared zrok URL. Update your application's MongoDB connection string to use `localhost:9191` as the MongoDB host.
