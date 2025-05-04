

# Google-Forms-MCP-Server

**A MCP Server to work with Google Forms API**

This project provides a server implementation that communicates with the Google Forms API to manage forms, process responses, and integrate seamlessly into other systems.

---

## Table of Contents

1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Installation](#installation)
4. [Usage](#usage)
5. [API Endpoints](#api-endpoints)
6. [Configuration](#configuration)
7. [Contributing](#contributing)
8. [License](#license)
9. [Acknowledgments](#acknowledgments)

---

## Features

- **Integration with Google Forms API**: Create, manage, and retrieve Google Forms programmatically.
- **Response Handling**: Efficiently process and store form responses.
- **Customizable MCP Server**: Easy-to-use API server tailored for Google Forms workflows.
- **100% Python**: Built entirely in Python for developers familiar with the language.
- **Extendable**: Add new features with ease.

---

## Technologies Used

- **Python**: The primary language for implementing the server.
- **Flask/Django/FastAPI** (or similar): Web framework for serving the API (specify the framework used in your implementation).
- **Google Forms API**: For interacting with Google Forms.

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/TaichKarna/Google-Forms-MCP-Server.git
   cd Google-Forms-MCP-Server
   ```

2. **Set up a virtual environment** (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google API credentials**:
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
   - Enable the Google Forms API.
   - Download the credentials JSON file and place it in the root of the project directory.
   - Update the `.env` file with the path to your credentials (see [Configuration](#configuration)).

5. **Run the server**:
   ```bash
   python app.py  # Adjust the filename as necessary
   ```

---

## Usage

Once the server is running, you can make requests to the API. Below are some example use cases:

- **Create a form**:
  ```bash
  curl -X POST http://localhost:5000/forms/create -d '{"title": "My Form"}'
  ```

- **Get form responses**:
  ```bash
  curl http://localhost:5000/forms/responses?formId=FORM_ID
  ```

Replace `FORM_ID` with your Google Form's ID.

---

## API Endpoints

Here are the key endpoints provided by the MCP Server:

### `/forms/create`
- **Method**: POST
- **Description**: Create a new Google Form.
- **Request Body**:
  ```json
  {
    "title": "Form Title",
    "description": "Form Description"
  }
  ```

### `/forms/responses`
- **Method**: GET
- **Description**: Retrieve responses for a specific form.
- **Query Parameters**:
  - `formId`: The ID of the Google Form.
  
_(Add more endpoints as necessary.)_

---

## Configuration

The server uses environment variables for configuration. Add a `.env` file in the root directory with the following keys:

```env
GOOGLE_API_CREDENTIALS=path/to/credentials.json
API_PORT=5000
DEBUG=true
```

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Add your feature description here"
   ```
4. Push to your forked repository:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Create a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

- [Google Cloud](https://cloud.google.com/) for the Forms API.
- Open-source contributors who made this project possible.

