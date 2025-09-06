#!/usr/bin/env python3
"""
MCP Server for Medicinal Product Mapper
Deployable via FastMCP Cloud for use with ChatGPT, Google Gemini, and Claude
"""

try:
    from fastmcp import FastMCP
except ImportError:
    # Fallback for testing without FastMCP installed
    class FastMCP:
        def __init__(self, name):
            self.name = name
        
        def tool(self):
            def decorator(func):
                return func
            return decorator
        
        def run(self):
            print(f"MCP Server '{self.name}' ready (FastMCP not installed - testing mode)")
from improved_medicinal_product_mapper import XMLMedicinalProductMapper
import json

# Initialize FastMCP server
server = FastMCP("Medicinal Product Mapper")

# Initialize the mapper
mapper = XMLMedicinalProductMapper()

@server.tool()
def map_medications_from_xml(xml_content: str) -> str:
    """
    Map substance names to SNOMED CT Concept IDs and ATC codes from XML input.
    
    Args:
        xml_content: XML content containing medication data with substance names
        
    Returns:
        JSON string with mapping results including SNOMED CT and ATC codes
    """
    try:
        # Parse XML and map medications
        medications, results = mapper.map_medications_from_xml(xml_content)
        
        if not medications:
            return json.dumps({
                "success": False,
                "error": "No medications found in XML input",
                "medications": [],
                "summary": {
                    "total": 0,
                    "found": 0,
                    "not_found": 0,
                    "success_rate": 0.0
                }
            }, indent=2)
        
        # Generate XML output
        output_xml = mapper.generate_xml_output(medications, results)
        
        # Prepare response data
        response_data = {
            "success": True,
            "xml_output": output_xml,
            "medications": [],
            "summary": {
                "total": len(medications),
                "found": sum(1 for result in results.values() if result['found']),
                "not_found": sum(1 for result in results.values() if not result['found']),
                "success_rate": (sum(1 for result in results.values() if result['found']) / len(medications)) * 100
            }
        }
        
        # Add medication details
        for medication in medications:
            substance_name = medication.substance
            result = results.get(substance_name, {})
            
            medication_data = {
                "sub_id": medication.sub_id,
                "substance": substance_name,
                "advice": medication.advice,
                "snomed_ct": result.get('conceptId', 'SNOMED CT not found') if result.get('found') else 'SNOMED CT not found',
                "atc_codes": mapper.get_atc_codes_from_felleskatalogen(substance_name),
                "found": result.get('found', False),
                "match_type": result.get('match_type', 'Not found')
            }
            
            # Add reference data if present
            if medication.ref_1_id:
                medication_data["ref_1_id"] = medication.ref_1_id
            if medication.ref_1_name:
                medication_data["ref_1_name"] = medication.ref_1_name
            if medication.ref_1_advice:
                medication_data["ref_1_advice"] = medication.ref_1_advice
            
            response_data["medications"].append(medication_data)
        
        return json.dumps(response_data, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error processing XML: {str(e)}",
            "medications": [],
            "summary": {
                "total": 0,
                "found": 0,
                "not_found": 0,
                "success_rate": 0.0
            }
        }, indent=2)

@server.tool()
def get_atc_codes(substance_name: str) -> str:
    """
    Get ATC codes for a specific substance from Felleskatalogen.
    
    Args:
        substance_name: Name of the substance to look up ATC codes for
        
    Returns:
        JSON string with ATC codes for the substance
    """
    try:
        atc_codes = mapper.get_atc_codes_from_felleskatalogen(substance_name)
        
        return json.dumps({
            "success": True,
            "substance": substance_name,
            "atc_codes": atc_codes,
            "source": "Felleskatalogen (https://www.felleskatalogen.no/medisin/substansregister/)"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "substance": substance_name,
            "error": f"Error looking up ATC codes: {str(e)}",
            "atc_codes": "ATC code not found"
        }, indent=2)

@server.tool()
def get_snomed_concept_id(substance_name: str) -> str:
    """
    Get SNOMED CT Concept ID for a specific substance.
    
    Args:
        substance_name: Name of the substance to look up SNOMED CT Concept ID for
        
    Returns:
        JSON string with SNOMED CT Concept ID and details
    """
    try:
        medicinal_product = mapper.find_medicinal_product_for_substance(substance_name)
        
        if medicinal_product:
            return json.dumps({
                "success": True,
                "substance": substance_name,
                "concept_id": medicinal_product.conceptId,
                "fsn": medicinal_product.fsn,
                "pt": medicinal_product.pt,
                "status": medicinal_product.definitionStatus,
                "effective_time": medicinal_product.effectiveTime,
                "match_type": mapper._classify_match(medicinal_product, substance_name),
                "source": "SNOMED CT Norwegian Edition"
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "substance": substance_name,
                "concept_id": "SNOMED CT not found",
                "error": "No medicinal product found for this substance",
                "source": "SNOMED CT Norwegian Edition"
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "substance": substance_name,
            "error": f"Error looking up SNOMED CT Concept ID: {str(e)}",
            "concept_id": "SNOMED CT not found"
        }, indent=2)

if __name__ == "__main__":
    server.run()
