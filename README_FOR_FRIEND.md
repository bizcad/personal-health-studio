Absolutely — here is a polished, user‑friendly **`FRIENDS_SETUP.md`** you can drop directly into your fork of the repo. It’s written for your two friends who know their way around PDFs, and can follow clear steps without needing to be modern developers.

It’s also structured so Claude Desktop can use it as a reference when helping them.

---

# FRIENDS_SETUP.md  
### *A simple guide to installing and using your personal Health Insight System*  
*(Built by Nicholas, powered by Claude + Snowflake)*

---

# 🧠 What This System Does

This project turns your health PDFs into something actually useful.

You can:

- Import your health records (PDFs from your provider)
- Store them in a secure personal database
- Ask questions in plain English, like:
  - “What’s my cholesterol trend over the last 5 years”
  - “Have my A1C levels improved”
  - “Show me abnormal labs in the last 12 months”
- Get charts, summaries, and insights instantly

You don’t need modern coding skills.  
If you can:

- Install a few tools  
- Copy/paste commands  
- Download a PDF  

…you’re good.

---

# 🧩 What You Need Installed

Please install these before starting:

### 1. **Claude Desktop**  
Download from Anthropic’s website. This is the app you’ll talk to.

### 2. **Node.js (LTS version)**  
Download from https://nodejs.org  
This runs the “MCP server” that connects Claude to your health data.

### 3. **Git**  
Download from https://git-scm.com  
This lets you download the project.

### 4. **A Snowflake Free‑Tier Account**  
This is your personal, secure database.  
Setup instructions are below — don’t worry, it’s easy.

---

# 📥 Step 1 — Download the Project

Open a terminal and run:

```bash
git clone <THE_REPO_URL_NICHOLAS_GIVES_YOU>
cd multi-agent-health-insight-system
```

That’s it. You now have the system on your machine.

---

# ❄️ Step 2 — Create Your Snowflake Account (Important)

This is the only part that requires a little attention.  
Follow these steps exactly.

### 2.1. Sign up

1. Go to Snowflake’s website  
2. Choose **Free Tier / Trial**
3. Pick:
   - **Cloud provider:** AWS, Azure, or GCP (any is fine)
   - **Region:** choose one close to you
4. Create your username + password

You’ll receive an account URL like:

```
https://xy12345.us-west-2.snowflakecomputing.com
```

Keep this handy.

---

# 🧊 Step 3 — Log Into Snowflake

1. Open your Snowflake account URL in a browser  
2. Log in  
3. You’ll see the **Snowsight** interface (Snowflake’s UI)

---

# 🏗️ Step 4 — Create Your Warehouse, Database, and Schema

In Snowflake:

1. Click **Projects → Worksheets**
2. Create a new SQL worksheet
3. Copy/paste this:

```sql
CREATE WAREHOUSE IF NOT EXISTS HEALTH_WH
  WITH WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

CREATE DATABASE IF NOT EXISTS HEALTH_DB;
CREATE SCHEMA IF NOT EXISTS HEALTH_DB.PUBLIC;

USE WAREHOUSE HEALTH_WH;
USE DATABASE HEALTH_DB;
USE SCHEMA HEALTH_DB.PUBLIC;
```

Click **Run**.

You now have:

- A compute engine (warehouse)
- A database
- A schema
- All ready for your health data

---

# 🧬 Step 5 — Create the Tables

Nicholas has included a file called:

```
schema/health_schema.sql
```

Open it, copy everything, and paste it into your Snowflake worksheet.

Click **Run**.

You should see messages like:

```
Table LAB_RESULTS created.
Table ENCOUNTERS created.
...
```

If you see that, you’re done.

---

# 🔐 Step 6 — Configure Your Local Credentials

In the project folder, create a file named:

```
.env
```

Put this inside (replace with your info):

```
SNOWFLAKE_ACCOUNT=<your_account_identifier>
SNOWFLAKE_USER=<your_username>
SNOWFLAKE_PASSWORD=<your_password>
SNOWFLAKE_WAREHOUSE=HEALTH_WH
SNOWFLAKE_DATABASE=HEALTH_DB
SNOWFLAKE_SCHEMA=PUBLIC
```

**Important:**  
Your account identifier is usually the part before `.snowflakecomputing.com`.  
Example:

```
xy12345.us-west-2
```

---

# 🛠️ Step 7 — Install the Tools

In the project folder:

```bash
npm install
```

This installs the MCP server.

---

# 🚀 Step 8 — Start the MCP Server

Run:

```bash
npx health-mcp
```

You should see:

- “Connected to Snowflake”
- “Listening on …”

Leave this terminal window open.

---

# 🤖 Step 9 — Connect MCP to Claude Desktop

In Claude Desktop:

1. Open **Settings**
2. Go to **Developer → MCP Servers**
3. Add a new server:
   - **Name:** `health-mcp`
   - **Command:** `npx health-mcp`
   - **Working directory:** the project folder

Claude will now see tools like:

- `import_health_pdf`
- `query_health_data`

---

# 📄 Step 10 — Import Your Health PDFs

1. Download your health PDFs from your provider  
2. Put them into:

```
data/raw/
```

3. Open Claude Desktop  
4. Start a chat with the “Health Extractor” agent  
5. Say:

> Please import `data/raw/my_health_export.pdf` using the health import tool.

Claude will:

- Read the PDF  
- Extract labs, vitals, meds, encounters  
- Insert them into Snowflake  

You can verify in Snowflake:

```sql
SELECT * FROM LAB_RESULTS LIMIT 10;
```

---

# 🔍 Step 11 — Ask Questions About Your Health

Now talk to the “Health Analyst” agent in Claude:

- “What’s my cholesterol trend over the last 5 years”
- “Have my A1C levels improved”
- “Show me abnormal labs in the last 12 months”
- “Summarize my health over the last 3 years”

Claude will:

- Translate your question into SQL  
- Run it on Snowflake  
- Summarize the results  

---

# 🎉 You’re Done

You now have a personal health insight system that:

- Reads your PDFs  
- Stores your data securely  
- Lets you ask questions in plain English  
- Gives you real insights instantly  

If you want to go deeper later:

- Nick can add RoadTrip’s `gpush` skill  
- You can switch to CockroachDB or Postgres  
- You can add charts, dashboards, or alerts  

But for now — enjoy your new health superpowers.

