# 🤖 LLM Instructions for Medicinal Product Mapper MCP Server

## 📋 **Server Overview**

This MCP server provides medicinal product mapping capabilities with SNOMED CT Concept IDs and ATC codes from Norwegian healthcare databases.

**Server URL**: `https://your-username.fastmcp.app` (replace with your actual FastMCP Cloud URL)

## 🛠️ **Available Tools**

### 1. `map_single_medication` ⭐ **RECOMMENDED FOR SINGLE SUBSTANCES**
**Purpose**: Lightweight mapping of individual substances
**Best for**: Single substance lookups, quick mapping, avoiding server overload
**Performance**: Fast, minimal resource usage

**Input Format**:
```json
{
  "substance_name": "Acetylsalisylsyre"
}
```

**Output**: JSON with SNOMED CT and ATC mapping for the single substance

### 2. `map_medications_from_xml` ⚠️ **USE SPARINGLY**
**Purpose**: Complete XML processing with SNOMED CT and ATC mapping
**Best for**: Processing multiple medications at once from XML input
**Performance**: Resource-intensive, limited to 10 medications by default (max 50)

**Input Format**:
```json
{
  "xml_content": "<XML>...</XML>"
}
```

**Example XML Input**:
```xml
<XML>
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<XML-File xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <Medication>
        <sub_id>Gk-07-gravid-112</sub_id>
        <substance>Abakavir</substance>
        <advice>Erfaring med bruk hos gravide er begrenset...</advice>
    </Medication>
    <Medication>
        <sub_id>Gk-07-gravid-143</sub_id>
        <substance>Acetylcystein</substance>
        <advice>Ingen holdepunkter for fosterskade</advice>
    </Medication>
</XML-File>
</XML>
```

**Output**: JSON with mapping results and generated XML output. Includes:
- `confidence`: numeric score reflecting match strength
- `candidates`: up to 3 alternative product candidates (conceptId, fsn, pt, score)

### 2. `get_atc_codes`
**Purpose**: Get ATC codes for a specific substance
**Best for**: Single substance ATC code lookup

**Input Format**:
```json
{
  "substance_name": "Acetylsalisylsyre"
}
```

**Output**: JSON with ATC codes from Felleskatalogen

### 3. `get_snomed_concept_id`
**Purpose**: Get SNOMED CT Concept ID for a specific substance
**Best for**: Single substance SNOMED CT lookup

**Input Format**:
```json
{
  "substance_name": "Xylometazolin"
}
```

**Output**: JSON with Concept ID and details

## 🎯 **Usage Guidelines for LLMs**
### New behavior and robustness
- The server uses language fallback (nb-x-sct, en-x-sct) when querying SNOMED CT.
- Two-step ontology search: finds substance concepts first, then products via ECL on `Has active ingredient`.
- Normalization (diacritics, whitespace) and targeted aliases improve recall.
- Confidence score and alternative candidates are provided when ambiguity exists.
- If you receive low confidence or no results, you may decide to retry with synonyms.

### **When to Use Each Tool**

1. **Use `map_single_medication`** ⭐ **PREFERRED** when:
   - User asks for mapping of a single substance
   - User provides one substance name
   - You want both SNOMED CT and ATC codes for one substance
   - **This is the most efficient tool for single substances**

2. **Use `map_medications_from_xml`** ⚠️ **ONLY** when:
   - User provides XML data with multiple medications (2+)
   - User specifically requests XML processing
   - You need to process more than 1 substance at once
   - **Limit to max 10 medications to avoid server overload**

3. **Use `get_atc_codes`** when:
   - User asks specifically for ATC codes only
   - User provides a single substance name
   - Quick ATC code lookup needed

4. **Use `get_snomed_concept_id`** when:
   - User asks specifically for SNOMED CT Concept ID only
   - User provides a single substance name
   - Quick SNOMED CT lookup needed

### **Common User Queries and Tool Selection**

| User Query | Recommended Tool | Reason |
|------------|------------------|---------|
| "Map Acetylsalisylsyre" | `map_single_medication` | Single substance, both codes |
| "What are the ATC codes for X?" | `get_atc_codes` | Specific ATC lookup only |
| "Find SNOMED CT ID for Y" | `get_snomed_concept_id` | Specific SNOMED lookup only |
| "Map these medications from XML" | `map_medications_from_xml` | Multiple medications in XML |
| "Get codes for multiple substances" | `map_single_medication` (multiple calls) | Individual lookups, more efficient |
| "Process this medication list" | `map_single_medication` (multiple calls) | More efficient than XML processing |

## 📊 **Expected Results**

### **Success Rates**
- **SNOMED CT**: ~60-70% for individual substances
- **ATC Codes**: ~90%+ for known substances
- **Drug Classes**: Not supported (use individual substances)

### **Response Format**
All tools return JSON with:
- `success`: boolean indicating if operation succeeded
- `error`: error message if failed
- Tool-specific data fields

## 🔍 **Substance Name Handling**

### **Norwegian vs English Names**
- **Try Norwegian names first**: "Acetylsalisylsyre" (not "Acetylsalicylic acid")
- **Fallback to English**: If Norwegian fails, try English equivalent
- **Common Norwegian names**:
  - Acetylsalisylsyre = Acetylsalicylic acid
  - Hydrokortison = Hydrocortisone
  - Oksytocin = Oxytocin

### **Drug Classes vs Individual Substances**
- **❌ Don't use**: "Antiviralemidler", "NSAID", "Cytostatika" (drug classes)
- **✅ Use instead**: Individual substances like "Abakavir", "Acetylsalisylsyre", "Cytarabin"

### Synonym expansion (LLM-driven)
- If the first attempt yields no/low-confidence results, try common synonyms or English names.
- Example: "Acetylsalisylsyre" → try "acetylsalicylic acid" or "aspirin".

## 🚨 **Error Handling**

### **Common Errors and Solutions**

1. **"SNOMED CT not found"**
   - Try English name if Norwegian failed
   - Check if it's a drug class (not supported)
   - Substance might not exist in Norwegian SNOMED CT

2. **"ATC code not found"**
   - Try alternative spelling
   - Check if substance exists in Felleskatalogen
   - May be a very new or uncommon substance

3. **XML parsing errors**
   - Validate XML format
   - Ensure proper encoding (UTF-8)
   - Check for malformed XML structure

## 💡 **Best Practices for LLMs**

### **1. Always Try Both Names**
```python
# Try Norwegian first
result = get_atc_codes("Acetylsalisylsyre")
if not result.success:
    # Fallback to English
    result = get_atc_codes("Acetylsalicylic acid")
```

### **2. Provide Context**
When presenting results, explain:
- What SNOMED CT Concept IDs are
- What ATC codes represent
- Success rates and limitations

### **3. Handle Multiple Substances**
For lists of substances:
- Use individual tool calls for better error handling
- Provide summary of results
- Highlight which substances were found/not found

### **4. User Education**
Explain to users:
- Why some substances aren't found (drug classes vs individual substances)
- The difference between SNOMED CT and ATC codes
- Data sources (Norwegian SNOMED CT, Felleskatalogen)

## 📝 **Example Interactions**

### **User**: "Get ATC codes for Abakavir, Acetylcystein, and Acetylsalisylsyre"

**LLM Response**:
I'll look up the ATC codes for each substance individually:

1. **Abakavir**: J05A F06, J05A R02, J05A R13
2. **Acetylcystein**: R05C B01, V03A B23  
3. **Acetylsalisylsyre**: B01A C06, B01A C30, N02B A01, N02B E51

All three substances were found in the Felleskatalogen database.

### **User**: "Process this XML with medication data"

**LLM Response**:
I'll process your XML data to map all substances to SNOMED CT Concept IDs and ATC codes. This will provide comprehensive mapping results for all medications in your XML.

[Uses `map_medications_from_xml` tool]

## 🔗 **Data Sources**

- **SNOMED CT**: Norwegian SNOMED CT Edition
- **ATC Codes**: Felleskatalogen (https://www.felleskatalogen.no/medisin/substansregister/)

## 📞 **Support**

If tools fail or return unexpected results:
1. Check substance name spelling
2. Try alternative names (Norwegian/English)
3. Verify it's an individual substance, not a drug class
4. Check if the substance exists in Norwegian healthcare databases
