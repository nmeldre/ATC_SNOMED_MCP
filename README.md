# Medicinal Product Mapper MCP Server

This MCP (Model Context Protocol) server provides medicinal product mapping capabilities with SNOMED CT Concept IDs and ATC codes from the Norwegian Felleskatalogen.

## Features

- **XML Processing**: Parse medication XML input and extract substance names
- **SNOMED CT Lookup**: Find medicinal product Concept IDs from Norwegian SNOMED CT
- **ATC Code Lookup**: Get ATC codes from Felleskatalogen website
- **Multiple ATC Codes**: Support for substances with multiple ATC classifications
- **Comprehensive Output**: Generate XML output with all mapping results

## Available Tools

### 1. `map_medications_from_xml`
Maps substance names to SNOMED CT Concept IDs and ATC codes from XML input.

**Input**: XML content containing medication data
**Output**: JSON with mapping results and generated XML output

### 2. `get_atc_codes`
Gets ATC codes for a specific substance from Felleskatalogen.

**Input**: Substance name
**Output**: JSON with ATC codes

### 3. `get_snomed_concept_id`
Gets SNOMED CT Concept ID for a specific substance.

**Input**: Substance name
**Output**: JSON with Concept ID and details

## Example XML Input Format

```xml
<XML>
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<XML-File xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <Medication>
        <sub_id>Gk-07-gravid-112</sub_id>
        <substance>Abakavir</substance>
        <advice>Erfaring med bruk hos gravide er begrenset...</advice>
    </Medication>
</XML-File>
</XML>
```

## Example Output

```json
{
  "success": true,
  "xml_output": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>...",
  "medications": [
    {
      "sub_id": "Gk-07-gravid-112",
      "substance": "Abakavir",
      "advice": "Erfaring med bruk hos gravide er begrenset...",
      "snomed_ct": "SNOMED CT not found",
      "atc_codes": "J05A F06, J05A R02, J05A R13",
      "found": false,
      "match_type": "Not found"
    }
  ],
  "summary": {
    "total": 1,
    "found": 0,
    "not_found": 1,
    "success_rate": 0.0
  }
}
```

## Deployment

This MCP server is designed to be deployed via FastMCP Cloud for use with:
- ChatGPT
- Google Gemini
- Claude

## Data Sources

- **SNOMED CT**: Norwegian SNOMED CT Edition
- **ATC Codes**: Felleskatalogen (https://www.felleskatalogen.no/medisin/substansregister/)

## Success Rates

Typical success rates:
- **SNOMED CT**: ~60-70% for individual substances
- **ATC Codes**: ~90%+ for known substances
- **Drug Classes**: Not supported (use individual substances instead)
