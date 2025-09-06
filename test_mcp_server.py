#!/usr/bin/env python3
"""
Test MCP Server for Medicinal Product Mapper
Simple version without FastMCP dependency for testing
"""

import json
import sys
from improved_medicinal_product_mapper import XMLMedicinalProductMapper

def test_map_medications_from_xml(xml_content: str) -> str:
    """Test function for mapping medications from XML"""
    try:
        mapper = XMLMedicinalProductMapper()
        medications, results = mapper.map_medications_from_xml(xml_content)
        
        if not medications:
            return json.dumps({
                "success": False,
                "error": "No medications found in XML input"
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
            
            response_data["medications"].append(medication_data)
        
        return json.dumps(response_data, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error processing XML: {str(e)}"
        }, indent=2)

def test_get_atc_codes(substance_name: str) -> str:
    """Test function for getting ATC codes"""
    try:
        mapper = XMLMedicinalProductMapper()
        atc_codes = mapper.get_atc_codes_from_felleskatalogen(substance_name)
        
        return json.dumps({
            "success": True,
            "substance": substance_name,
            "atc_codes": atc_codes,
            "source": "Felleskatalogen"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "substance": substance_name,
            "error": f"Error looking up ATC codes: {str(e)}"
        }, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_mcp_server.py <function> <args>")
        print("Functions: map_medications_from_xml, get_atc_codes")
        sys.exit(1)
    
    function = sys.argv[1]
    
    if function == "map_medications_from_xml":
        if len(sys.argv) < 3:
            print("Usage: python test_mcp_server.py map_medications_from_xml '<xml_content>'")
            sys.exit(1)
        xml_content = sys.argv[2]
        result = test_map_medications_from_xml(xml_content)
        print(result)
    
    elif function == "get_atc_codes":
        if len(sys.argv) < 3:
            print("Usage: python test_mcp_server.py get_atc_codes '<substance_name>'")
            sys.exit(1)
        substance_name = sys.argv[2]
        result = test_get_atc_codes(substance_name)
        print(result)
    
    else:
        print(f"Unknown function: {function}")
        sys.exit(1)
