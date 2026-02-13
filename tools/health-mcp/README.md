# claude_desktop_config.json - MCP Server Configuration

This file configures Claude Desktop to connect to the Health MCP server for data import and querying.

## Location
`~/.claude_desktop_config.json` (macOS/Linux) or `%APPDATA%\claude\claude_desktop_config.json` (Windows)

## Template Configuration

Replace credentials with your actual Snowflake account details:

```json
{
  "mcpServers": {
    "health-intelligence": {
      "command": "/path/to/.local/bin/uv",
      "args": [
        "--directory",
        "/path/to/tools/health-mcp",
        "run",
        "src/health_mcp.py"
      ],
      "env": {
        "SNOWFLAKE_ACCOUNT": "your-account-id",
        "SNOWFLAKE_USER": "your-username",
        "SNOWFLAKE_WAREHOUSE": "COMPUTE_WH",
        "SNOWFLAKE_DATABASE": "HEALTH_INTELLIGENCE",
        "SNOWFLAKE_SCHEMA": "HEALTH_RECORDS",
        "SNOWFLAKE_ROLE": "ACCOUNTADMIN",
        "SNOWFLAKE_PRIVATE_KEY_PATH": "/path/to/rsa_key.p8"
      }
    }
  }
}
```

## Configuration Steps

### 1. Snowflake Setup
- [ ] Create Snowflake account (free tier at https://signup.snowflake.com)
- [ ] Note your Account ID (from account URL)
- [ ] Create a warehouse named `COMPUTE_WH`
- [ ] Generate RSA private key for authentication
- [ ] Store key path in `SNOWFLAKE_PRIVATE_KEY_PATH`

### 2. Generate RSA Private Key
```bash
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
```

### 3. Configure Claude Desktop
- [ ] Edit `.claude_desktop_config.json` with your values
- [ ] Update `SNOWFLAKE_ACCOUNT` with your account ID
- [ ] Update paths to match your system
- [ ] Verify Python uv installation: `which uv` or `where uv`

### 4. Install MCP Server
```bash
cd tools/health-mcp
uv sync
```

### 5. Test Connection
Restart Claude Desktop and use the Health Analyst Agent to verify connection:
- Agent should report "Tools available"
- Both tools should be listed:
  - `snowflake_import_analyze_health_records_v2`
  - `execute_health_query_v2`

## Troubleshooting

### "MCP server not found"
- Check uv path: `which uv`
- Verify health-mcp directory exists
- Ensure uv.lock is present in tools/health-mcp/

### "Snowflake connection refused"
- Verify Account ID is correct
- Check username and role have proper permissions
- Confirm private key file exists and is readable
- Verify SNOWFLAKE_ACCOUNT format (e.g., "xy12345.us-east-1")

### "Tools not available"
- Check MCP server logs in Claude Desktop
- Verify environment variables are set correctly
- Ensure HEALTH_INTELLIGENCE database exists
- Test Snowflake connection manually with snowsql

## Production Checklist

Before sharing with friends:
- [ ] Test with sample health data
- [ ] Verify data is imported correctly
- [ ] Test natural language queries work
- [ ] Confirm no data leaks in logs
- [ ] Document credential setup for friends
- [ ] Create safe backup of RSA private key
- [ ] Test full end-to-end workflow
