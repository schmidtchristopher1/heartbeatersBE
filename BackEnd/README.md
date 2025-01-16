## Getting Started

Follow these steps to set up the project for development.

### Prerequisites

- **Python 3.7+**
- **Virtual Environment** (recommended)
- **Flask** and related dependencies (listed in `requirements.txt`)

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/schmidtchristopher1/heartbeatersBE.git
   cd BackEnd
   ```

2. **Set Up a Virtual Environment**

   ```bash
   python -m venv .venv
   ```

3. **Activate the Virtual Environment**

   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Environment Variables**

   Create an `.env` file in the root directory and add necessary configurations:

   ```plaintext
    SECRET_KEY=your_secret_key
    JWT_SECRET_KEY=your_jwt_secret_key
    DATABASE_URI=sqlite:///heart_beaters.db
    FLASK_APP=app.py
    FLASK_ENV=production/development
    UPLOAD_FOLDER=path_to_your_upload_folder

   ```

## Running the Application

### Development Mode

In development, the application runs with debug mode enabled.

```bash
flask run
```

Visit `http://127.0.0.1:5000` in your browser to view the application.

### Production Mode

For production, set `FLASK_ENV=production` in the `.env` file to disable debug mode and use production settings:

```bash
export FLASK_ENV=production
flask run
```

### Accessing Swagger Documentation

> Note: Swagger documentation is currently not functioning and will be fixed in a future update.

Swagger documentation will be available at `/apidocs` by default:

- **Development**: [http://127.0.0.1:5000/apidocs](http://127.0.0.1:5000/apidocs)
- **Production**: Replace `127.0.0.1:5000` with your production domain.

### Configurations (`config.py`)

- **DevelopmentConfig**: Debug mode, connects to the development database.
- **ProductionConfig**: Debug mode off, connects to the production database.
- `FLASK_ENV` environment variable determines which configuration is loaded.

### Swagger Documentation (`swagger/guides.py`)

- `guides.py` contains descriptions for Swagger, keeping the API code clean.
- Each endpoint in `api.py` imports relevant descriptions from `guides.py`.

### Testing

All tests are located in the `tests` folder. Run tests with:

```bash
pytest
```

## Example Usage

Try accessing the API endpoint after starting the server:

**Status Endpoint**

```bash
curl http://127.0.0.1:5000/status
```
