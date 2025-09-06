# 🔧 Gemini CLI Setup for MCP Server

## 📋 **Current Issues**

1. **Authentication**: Gemini CLI needs API key configuration
2. **MCP Server URL**: Wrong URL format being used
3. **Tool Usage**: CLI doesn't know how to call MCP tools properly

## 🛠️ **Setup Steps**

### **Step 1: Configure Gemini API Key**

You need to set up authentication for Gemini CLI. Choose one of these methods:

#### **Option A: Environment Variable**
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

#### **Option B: Settings File**
Edit `/Users/nikolai/.gemini/settings.json`:
```json
{
  "auth": {
    "method": "api_key",
    "api_key": "your-gemini-api-key-here"
  }
}
```

### **Step 2: Add MCP Server**

```bash
gemini mcp add nmeldre https://your-username.fastmcp.app
```

Replace `your-username` with your actual FastMCP Cloud username.

### **Step 3: Test MCP Server**

```bash
gemini -p "Use the nmeldre MCP server to get ATC codes for Abakavir"
```

## 🎯 **Correct Usage Examples**

### **Single Substance Lookup**
```bash
gemini -p "Use the nmeldre server to get ATC codes for Acetylsalisylsyre"
```

### **Multiple Substances**
```bash
gemini -p "Use the nmeldre server to get ATC codes for these substances: Abakavir, Acetylcystein, Acetylsalisylsyre"
```

### **XML Processing**
```bash
gemini -p "Use the nmeldre server to process this XML and map all substances to SNOMED CT and ATC codes: <XML>...</XML>"
```

## 🔍 **Troubleshooting**

### **Error: "Request failed with status code 406"**
- **Cause**: Wrong URL format
- **Solution**: Use `https://your-username.fastmcp.app` (not `/mcp` suffix)

### **Error: "Please set an Auth method"**
- **Cause**: Missing API key
- **Solution**: Set `GEMINI_API_KEY` environment variable or configure settings.json

### **Error: "Unknown arguments: server, search"**
- **Cause**: Wrong command syntax
- **Solution**: Use `-p` flag with natural language prompts

## 📝 **Alternative: Direct Tool Testing**

If Gemini CLI continues to have issues, you can test your MCP server directly:

### **Test ATC Codes**
```bash
curl -X POST https://your-username.fastmcp.app/tools/get_atc_codes \
  -H "Content-Type: application/json" \
  -d '{"substance_name": "Abakavir"}'
```

### **Test SNOMED CT**
```bash
curl -X POST https://your-username.fastmcp.app/tools/get_snomed_concept_id \
  -H "Content-Type: application/json" \
  -d '{"substance_name": "Xylometazolin"}'
```

## 🎯 **Expected Results**

### **ATC Codes Response**
```json
{
  "success": true,
  "substance": "Abakavir",
  "atc_codes": "J05A F06, J05A R02, J05A R13",
  "source": "Felleskatalogen"
}
```

### **SNOMED CT Response**
```json
{
  "success": true,
  "substance": "Xylometazolin",
  "concept_id": "777959005",
  "fsn": "Product containing only xylometazoline (medicinal product)",
  "pt": "Xylometazoline only product",
  "match_type": "Exact 'Product containing only' match"
}
```

## 🚀 **Next Steps**

1. **Get Gemini API Key**: Sign up at Google AI Studio
2. **Configure Authentication**: Set up API key as shown above
3. **Add MCP Server**: Use correct FastMCP Cloud URL
4. **Test Functionality**: Try the examples above
5. **Use in Conversations**: Ask natural language questions about medicinal products
