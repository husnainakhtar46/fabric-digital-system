# Google Cloud & Credentials Setup Guide

Follow these exact steps to get your `credentials.json` file and set up access.

## Step 1: Create a Project
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Click the project dropdown in the top-left (next to the Google Cloud logo).
3.  Click **New Project**.
4.  Name it "FabricDigital" (or anything you like) and click **Create**.
5.  Wait a moment, then select the new project from the notification bell or the dropdown.

## Step 2: Enable APIs
You need to tell Google this project is allowed to use Sheets and Drive.
1.  In the search bar at the top, type **"Google Sheets API"**.
2.  Click the result **Google Sheets API**.
3.  Click **Enable**.
4.  Once enabled, go back to the search bar.
5.  Type **"Google Drive API"**.
6.  Click the result **Google Drive API**.
7.  Click **Enable**.

## Step 3: Create a Service Account
This creates the "robot" user that will act as your agent.
1.  In the search bar, type **"Credentials"** and select **Credentials (APIs & Services)**.
2.  Click **+ CREATE CREDENTIALS** (top of the screen).
3.  Select **Service Account**.
4.  **Name**: `fabric-agent`.
5.  Click **Create and Continue**.
6.  **Role**: Search for **Editor** (Basic > Editor) and select it. This gives read/write permission.
7.  Click **Continue** and then **Done**.

## Step 4: Generate the Key (JSON)
1.  You should now see your new service account in the list (e.g., `fabric-agent@your-project.iam.gserviceaccount.com`).
2.  Click on the **Email address** of the service account to open its details.
3.  Go to the **KEYS** tab (top menu bar).
4.  Click **ADD KEY** > **Create new key**.
5.  Select **JSON**.
6.  Click **Create**.
7.  A file will automatically download to your computer. **Keep this safe!**

## Step 5: Install the Credential
1.  Find the downloaded file (it will have a long name like `project-id-12345.json`).
2.  **Rename** the file to exactly: `credentials.json`.
3.  **Move** this file into your project folder: `d:\Coding\Fabric\`.

## Step 6: Share Access (CRITICAL)
Your "robot" service account has an email address, but it cannot see your private files unless you share them.
1.  Open `credentials.json` (you can use Notepad) and look for the field `"client_email"`. It looks like `fabric-agent@...`. **Copy this email**.
2.  **Go to Google Drive**:
    *   **Sheet**: Create a new Google Sheet (or open your existing one). Click **Share** (top right), paste the client email, make sure it says **Editor**, and click **Send** (uncheck "Notify people" if you want).
    *   **Folder**: Create a new Folder for your images. Right-click the folder, select **Share**, paste the client email, make sure it says **Editor**, and click **Send**.

## Verification
You are done! Now run the test script in your terminal to confirm:
```powershell
cd d:\Coding\Fabric
python test_connection.py
```
