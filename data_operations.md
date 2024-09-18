# Data Operations

### Data Download

The FastAPI application includes endpoints to access a Google Drive folder and download all documents within it using Python.

### Prerequisites

1. **Google Cloud Project Setup:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project or select an existing one.
   - Navigate to **API & Services > Library**, and enable the Google Drive API.
   - Go to **API & Services > Credentials**, click on **Create Credentials**, and choose **OAuth 2.0 Client IDs**.
     - Select "User data" as the type of data you will be accessing.
     - Set up the OAuth consent screen, providing necessary information such as application name and contact information.
     - Add the scope: `https://www.googleapis.com/auth/drive.readonly`.
     - Choose "Web application" as the application type.
     - Provide the authorized redirect URIs (e.g., `http://localhost:8000` for development).
   - Download the JSON file containing your client secret and rename it to `credentials.json`.
   - Go to the OAuth consent screen of the [Google Cloud Console](https://console.cloud.google.com/) and make your app external, so any user can use it.

2. **Install Necessary Libraries:**
   - If you installed the project requirements with `requirements.txt`, you don't need to do this step separately.
   - The necessary Python libraries will be installed as part of the project dependencies.

### Usage

1. **Start the FastAPI Server:**
   - Run the FastAPI server using `uvicorn`:
     ```bash
     uvicorn app.api.app:app --reload
     ```

2. **Authentication:**
   - Visit `http://localhost:8000/gdrive/authorize` to initiate the OAuth flow.
   - Log in to your Google account and authorize access.
   - The authentication tokens will be saved to `token.pickle` for future use.

3. **Download Files:**
   - Use the `/gdrive/download_files/{folder_id}` endpoint to download files from a specified Google Drive folder.
   - Replace `{folder_id}` with the actual ID of the Google Drive folder you want to access.
   - The files will be downloaded to the `data/raw_data` directory.

### Notes

- The application is designed to download non-folder files only. Ensure that the folder contains the files you wish to download.
- The downloaded files will be saved in a local directory named `data/raw_data`. The directory will be created if it doesn't exist.
