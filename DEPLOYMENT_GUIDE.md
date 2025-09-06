# 🚀 MCP Deployment Guide for Medicinal Product Mapper

This guide will help you deploy your medicinal product mapper as an MCP server using FastMCP Cloud for use with ChatGPT, Google Gemini, and Claude.

## 📋 Prerequisites

1. **FastMCP Account**: Sign up at [FastMCP Cloud](https://gofastmcp.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Python 3.9+**: Ensure your environment supports the required Python version

## 📁 Files Created for MCP Deployment

### 1. `fastmcp.json` - Configuration File
```json
{
  "name": "medicinal-product-mapper",
  "version": "1.0.0",
  "description": "XML-based medicinal product mapper with SNOMED CT and ATC code lookup",
  "entrypoint": "mcp_server.py",
  "transport": {
    "type": "http"
  },
  "dependencies": [
    "requests",
    "xml.etree.ElementTree"
  ],
  "tools": [...]
}
```

### 2. `mcp_server.py` - MCP Server Implementation
- Wraps your existing mapper functionality
- Provides 3 tools: `map_medications_from_xml`, `get_atc_codes`, `get_snomed_concept_id`
- Returns JSON responses for easy parsing by AI models

### 3. `requirements_mcp.txt` - Dependencies
```
fastmcp>=2.12.0
requests>=2.31.0
```

## 🛠️ Deployment Steps

### Step 1: Prepare Your Repository
1. Ensure all files are in your GitHub repository:
   - `improved_medicinal_product_mapper.py` (your main script)
   - `mcp_server.py` (MCP wrapper)
   - `fastmcp.json` (configuration)
   - `requirements_mcp.txt` (dependencies)

### Step 2: Deploy to FastMCP Cloud
1. **Login to FastMCP Cloud**: Go to [gofastmcp.com](https://gofastmcp.com)
2. **Create New Server**: Click "Deploy New Server"
3. **Connect Repository**: Link your GitHub repository
4. **Configure Deployment**:
   - **Entry Point**: `mcp_server.py`
   - **Configuration**: Uses `fastmcp.json`
   - **Dependencies**: Automatically installs from `requirements_mcp.txt`

### Step 3: Test Your Deployment
1. **Get Server URL**: FastMCP Cloud will provide a URL for your server
2. **Test Tools**: Use the FastMCP Cloud interface to test your tools
3. **Verify Functionality**: Ensure all 3 tools work correctly

## 🔧 Available Tools

### 1. `map_medications_from_xml`
**Purpose**: Complete XML processing with SNOMED CT and ATC mapping
**Input**: XML content with medication data
**Output**: JSON with mapping results and generated XML

**Example Usage in AI Chat**:
```
"Map these medications from XML: <XML>...</XML>"
```

### 2. `get_atc_codes`
**Purpose**: Get ATC codes for a specific substance
**Input**: Substance name
**Output**: JSON with ATC codes

**Example Usage in AI Chat**:
```
"What are the ATC codes for Acetylsalisylsyre?"
```

### 3. `get_snomed_concept_id`
**Purpose**: Get SNOMED CT Concept ID for a substance
**Input**: Substance name
**Output**: JSON with Concept ID and details

**Example Usage in AI Chat**:
```
"What is the SNOMED CT Concept ID for Xylometazolin?"
```

## 🤖 Integration with AI Platforms

### ChatGPT
1. **Add MCP Server**: In ChatGPT settings, add your FastMCP Cloud URL
2. **Enable Tools**: The tools will appear in ChatGPT's function calling
3. **Use in Conversations**: ChatGPT can now call your medicinal product mapper

### Google Gemini
1. **Configure MCP**: Add your server URL to Gemini's MCP configuration
2. **Access Tools**: Gemini will have access to all 3 tools
3. **Natural Language**: Ask questions about medicinal products naturally

### Claude
1. **MCP Integration**: Claude supports MCP servers natively
2. **Tool Access**: All tools will be available in Claude conversations
3. **Complex Queries**: Claude can handle complex XML processing requests

## 📊 Expected Performance

### Success Rates
- **SNOMED CT Mapping**: ~60-70% for individual substances
- **ATC Code Lookup**: ~90%+ for known substances
- **XML Processing**: 100% for valid XML input

### Response Times
- **Single Substance Lookup**: 2-5 seconds
- **XML Processing**: 5-15 seconds (depending on number of substances)
- **ATC Code Lookup**: 1-3 seconds

## 🔍 Example Interactions

### ChatGPT Example
**User**: "I have this XML with medication data, can you map the substances to SNOMED CT and ATC codes?"

**ChatGPT**: *Uses `map_medications_from_xml` tool*
"I've processed your XML and found 7 out of 13 substances with SNOMED CT Concept IDs. Here are the results..."

### Claude Example
**User**: "What are the ATC codes for Acetylsalisylsyre and how does it compare to other NSAIDs?"

**Claude**: *Uses `get_atc_codes` tool*
"Acetylsalisylsyre has ATC codes: B01A C06, B01A C30, N02B A01, N02B E51. This shows it's classified as both an antiplatelet agent and an analgesic..."

## 🚨 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are in `requirements_mcp.txt`
2. **Timeout Issues**: FastMCP Cloud has timeout limits for long-running operations
3. **Memory Limits**: Large XML files may hit memory constraints

### Debugging
1. **Test Locally**: Use `test_mcp_server.py` to test functionality
2. **Check Logs**: FastMCP Cloud provides detailed logs
3. **Validate JSON**: Ensure your tools return valid JSON

## 📈 Monitoring and Analytics

FastMCP Cloud provides:
- **Usage Analytics**: Track tool usage across AI platforms
- **Performance Metrics**: Monitor response times and success rates
- **Error Logging**: Detailed error logs for debugging
- **Cost Tracking**: Monitor API usage and costs

## 🔄 Updates and Maintenance

### Updating Your Server
1. **Push Changes**: Update your GitHub repository
2. **Redeploy**: FastMCP Cloud will automatically redeploy
3. **Test**: Verify changes work correctly

### Adding New Tools
1. **Update `fastmcp.json`**: Add new tool definitions
2. **Implement in `mcp_server.py`**: Add the tool function
3. **Deploy**: Push changes to trigger redeployment

## 🎯 Best Practices

1. **Error Handling**: Always return valid JSON, even for errors
2. **Input Validation**: Validate inputs before processing
3. **Performance**: Optimize for the most common use cases
4. **Documentation**: Keep tool descriptions clear and helpful
5. **Testing**: Test thoroughly before deployment

## 📞 Support

- **FastMCP Documentation**: [gofastmcp.com/docs](https://gofastmcp.com/docs)
- **Community**: FastMCP Discord/GitHub discussions
- **Issues**: Report issues in your GitHub repository

---

Your medicinal product mapper is now ready to be deployed as an MCP server and used across multiple AI platforms! 🎉
