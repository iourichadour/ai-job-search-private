# Job Scout Agent: Gmail Parser & Authentication Guide

This module connects securely to your Gmail inbox, queries for unread job notifications from LinkedIn and Indeed, automatically extracts the hidden tracking URLs, and prepares a local queue for the AI agent to evaluate.

---

## 1. Google Cloud Console Setup

To let the Python script communicate with your inbox, you must generate desktop application credentials through Google Cloud.

### Step 1: Create a Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown in the top left and select **New Project**.
3. Name your project (e.g., `Job-Scout-Agent`) and click **Create**.

### Step 2: Enable the Gmail API
1. In the top search bar, search for **Gmail API**.
2. Click on the Gmail API result and click the blue **Enable** button.

### Step 3: Configure the OAuth Consent Screen
1. From the left sidebar, navigate to **APIs & Services** > **OAuth consent screen**.
2. Select **External** as the User Type and click **Create**.
3. Fill in the required fields:
   * **App name:** `Job Scout Agent`
   * **User support email:** Your Gmail address
   * **Developer contact information:** Your Gmail address
4. Click **Save and Continue** through the Scopes screen (you do not need to add explicit scopes here).
5. **Crucial Step:** On the **Test users** screen, click **+ Add Users**, type your exact Gmail address, and click **Save**. (If you skip this, your authentication will fail with a "403 Access Blocked" error).
6. Click **Save and Continue** to finish.

### Step 4: Generate Credentials
1. From the left sidebar, navigate to **APIs & Services** > **Credentials**.
2. Click **+ Create Credentials** at the top and choose **OAuth client ID**.
3. Set the Application type dropdown to **Desktop app**.
4. Name it (e.g., `Job Scout CLI`) and click **Create**.
5. Find your newly created client under "OAuth 2.0 Client IDs", click the **Download JSON** icon on the far right, rename the downloaded file to exactly `credentials.json`, and drop it into your root repository folder (`C:\Development\ai-job-search-private\credentials.json`).

---

## 2. Installation & First Run

1. Ensure your dependencies are installed:
   ```bash
   pip install -r requirements.txt