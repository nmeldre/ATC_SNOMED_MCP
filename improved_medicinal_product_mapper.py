#!/usr/bin/env python3
"""
XML-based Medicinal Product Mapper
Accepts XML input and generates XML output with SNOMED CT and ATC codes
"""

import requests
import json
import sys
import xml.etree.ElementTree as ET
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


@dataclass
class MedicinalProduct:
    """Represents a medicinal product from the API response"""
    conceptId: str
    fsn: str
    pt: str
    active: bool
    definitionStatus: str
    effectiveTime: str


@dataclass
class MedicationData:
    """Represents medication data from XML input"""
    sub_id: str
    substance: str
    advice: str
    ref_1_id: Optional[str] = None
    ref_1_name: Optional[str] = None
    ref_1_advice: Optional[str] = None


class XMLMedicinalProductMapper:
    """XML-based mapper with SNOMED CT and ATC code lookup"""
    
    def __init__(self, base_url: str = "http://dailybuild.terminologi.helsedirektoratet.no"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'XML-Medicinal-Product-Mapper/1.0'
        })
        self._cache = {}
        self._atc_cache = {}
    
    def find_medicinal_product_for_substance(self, substance_name: str) -> Optional[MedicinalProduct]:
        """Find the medicinal product Concept ID using multiple search strategies"""
        if substance_name in self._cache:
            return self._cache[substance_name]
        
        # Strategy 1: Search for "Product containing only [substance]"
        product = self._search_with_strategy_1(substance_name)
        if product:
            self._cache[substance_name] = product
            return product
        
        # Strategy 2: Search for "Product containing [substance]"
        product = self._search_with_strategy_2(substance_name)
        if product:
            self._cache[substance_name] = product
            return product
        
        # Strategy 3: Search with broader terms
        product = self._search_with_strategy_3(substance_name)
        if product:
            self._cache[substance_name] = product
            return product
        
        self._cache[substance_name] = None
        return None
    
    def _search_with_strategy_1(self, substance_name: str) -> Optional[MedicinalProduct]:
        """Strategy 1: Search for exact 'Product containing only [substance]'"""
        search_terms = [
            f"Product containing only {substance_name}",
            f"Product containing only {substance_name.lower()}",
            f"Product containing only {substance_name.title()}"
        ]
        
        for search_term in search_terms:
            products = self._search_medicinal_products(search_term)
            for product in products:
                if self._is_exact_only_match(product, substance_name):
                    return product
        
        return None
    
    def _search_with_strategy_2(self, substance_name: str) -> Optional[MedicinalProduct]:
        """Strategy 2: Search for 'Product containing [substance]' and find the best match"""
        search_terms = [
            substance_name,
            substance_name.lower(),
            substance_name.title()
        ]
        
        best_match = None
        best_score = 0
        
        for search_term in search_terms:
            products = self._search_medicinal_products(search_term)
            for product in products:
                score = self._calculate_match_score(product, substance_name)
                if score > best_score:
                    best_score = score
                    best_match = product
        
        return best_match
    
    def _search_with_strategy_3(self, substance_name: str) -> Optional[MedicinalProduct]:
        """Strategy 3: Broader search with substance name variations"""
        # Try common variations and synonyms
        variations = self._get_substance_variations(substance_name)
        
        for variation in variations:
            products = self._search_medicinal_products(variation)
            for product in products:
                if self._is_good_match(product, substance_name):
                    return product
        
        return None
    
    def _search_medicinal_products(self, search_term: str, limit: int = 100) -> List[MedicinalProduct]:
        """Search the medicinal product API"""
        url = f"{self.base_url}/snowstorm/snomed-ct/MAIN%2FSNOMEDCT-NO/concepts"
        
        # ECL query for medicinal products
        ecl_query = f"< 763158003 |Medicinal product| MINUS (* : 411116001 |Has manufactured dose form| = *)"
        
        params = {
            'activeFilter': 'true',
            'term': search_term,
            'ecl': ecl_query,
            'offset': 0,
            'limit': limit
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            products = []
            
            for item in data.get('items', []):
                product = MedicinalProduct(
                    conceptId=item.get('conceptId', ''),
                    fsn=item.get('fsn', {}).get('term', ''),
                    pt=item.get('pt', {}).get('term', ''),
                    active=item.get('active', False),
                    definitionStatus=item.get('definitionStatus', ''),
                    effectiveTime=item.get('effectiveTime', '')
                )
                products.append(product)
            
            return products
            
        except Exception as e:
            print(f"Error searching for '{search_term}': {e}")
            return []
    
    def _is_exact_only_match(self, product: MedicinalProduct, substance_name: str) -> bool:
        """Check if this is an exact 'Product containing only [substance]' match"""
        fsn = product.fsn.lower()
        substance_lower = substance_name.lower()
        
        # Look for exact "Product containing only [substance]" pattern
        exact_pattern = f"product containing only {substance_lower}"
        return exact_pattern in fsn
    
    def _calculate_match_score(self, product: MedicinalProduct, substance_name: str) -> int:
        """Calculate a match score for a product"""
        fsn = product.fsn.lower()
        pt = product.pt.lower()
        substance_lower = substance_name.lower()
        
        score = 0
        
        # Highest priority: "Product containing only [substance]"
        if f"product containing only {substance_lower}" in fsn:
            score += 100
        elif f"product containing only {substance_lower}" in pt:
            score += 100
        
        # High priority: "Product containing only [substance] (medicinal product)"
        elif f"product containing only {substance_lower}" in fsn and "(medicinal product)" in fsn:
            score += 90
        
        # Medium priority: Contains the substance name
        elif substance_lower in fsn:
            score += 50
        
        # Lower priority: Partial matches
        elif any(word in fsn for word in substance_lower.split()):
            score += 25
        
        return score
    
    def _is_good_match(self, product: MedicinalProduct, substance_name: str) -> bool:
        """Check if this is a good match for the substance"""
        score = self._calculate_match_score(product, substance_name)
        return score >= 50  # Require at least medium priority
    
    def _get_substance_variations(self, substance_name: str) -> List[str]:
        """Get common variations of a substance name"""
        variations = [substance_name]
        
        # Add common variations
        if substance_name.lower() == "hydrokodon":
            variations.extend(["hydrocodone", "hydrocodone bitartrate"])
        elif substance_name.lower() == "hydrokortison":
            variations.extend(["hydrocortisone", "cortisol"])
        elif substance_name.lower() == "artemeter":
            variations.extend(["artemether"])
        elif substance_name.lower() == "ofloksacin":
            variations.extend(["ofloxacin"])
        
        return variations
    
    def get_atc_codes_from_felleskatalogen(self, substance_name: str) -> str:
        """Get ATC codes from Felleskatalogen website"""
        if substance_name in self._atc_cache:
            return self._atc_cache[substance_name]
        
        try:
            # Search for the substance on Felleskatalogen
            search_url = "https://www.felleskatalogen.no/medisin/substansregister/"
            
            # Try to find the substance page directly
            substance_url = f"https://www.felleskatalogen.no/medisin/substansregister/{substance_name.lower()}"
            
            response = self.session.get(substance_url, timeout=10)
            
            if response.status_code == 200:
                atc_codes = self._extract_atc_codes_from_html(response.text, substance_name)
                if atc_codes:
                    self._atc_cache[substance_name] = atc_codes
                    return atc_codes
            
            # If direct URL doesn't work, try searching
            search_response = self.session.get(search_url, timeout=10)
            if search_response.status_code == 200:
                # Look for the substance in the search results
                atc_codes = self._search_substance_in_html(search_response.text, substance_name)
                if atc_codes:
                    self._atc_cache[substance_name] = atc_codes
                    return atc_codes
            
            # Fallback to predefined ATC codes
            fallback_codes = self._get_fallback_atc_codes(substance_name)
            self._atc_cache[substance_name] = fallback_codes
            return fallback_codes
            
        except Exception as e:
            print(f"Warning: Could not fetch ATC codes for '{substance_name}': {e}")
            fallback_codes = self._get_fallback_atc_codes(substance_name)
            self._atc_cache[substance_name] = fallback_codes
            return fallback_codes
    
    def _extract_atc_codes_from_html(self, html_content: str, substance_name: str) -> str:
        """Extract ATC codes from HTML content"""
        atc_codes = []
        
        # Look for ATC-koder pattern in the HTML
        atc_pattern = r'ATC-koder:\s*([^<]+)'
        matches = re.findall(atc_pattern, html_content, re.IGNORECASE)
        
        for match in matches:
            # Split by comma and clean up each code
            codes = [code.strip() for code in match.split(',')]
            atc_codes.extend(codes)
        
        # Remove duplicates and empty strings
        atc_codes = list(set([code for code in atc_codes if code]))
        
        if atc_codes:
            return ', '.join(atc_codes)
        return ""
    
    def _search_substance_in_html(self, html_content: str, substance_name: str) -> str:
        """Search for substance in HTML content and extract ATC codes"""
        # Look for the substance name in the HTML
        if substance_name.lower() in html_content.lower():
            return self._extract_atc_codes_from_html(html_content, substance_name)
        return ""
    
    def _get_fallback_atc_codes(self, substance_name: str) -> str:
        """Fallback ATC codes for known substances"""
        fallback_codes = {
            "Abakavir": "J05A F06, J05A R02, J05A R13",
            "Acetylcystein": "R05C B01, V03A B23",
            "Acetylsalisylsyre": "B01A C06, B01A C30, N02B A01, N02B E51",
            "Acitretin": "D05B B02",
            "Cytarabin": "L01B C01, L01X Y01",
            "Oksytocin": "H01B B02",
            "Caspofungin": "J02A X04",
            "Cetylpyridin": "D08A J03",
            "Lanreotid": "H01C B03",
            "Litium": "N05A N01",
            "Xylometazolin": "R01A A07",
            "Zanamivir": "J05A H01",
            "Ziprasidon": "N05A E04",
            "Nafarelin": "H01C C01",
            "Vankomycin": "J01X A01",
            "Verapamil": "C08D A01",
            "Vitamin D": "A11C C05",
            "Skopolamin": "A03B A01, S01F A01",
            "Mykofenolat": "L04A A06",
            "Vitamin K": "B02B A01"
        }
        
        return fallback_codes.get(substance_name, "ATC code not found")
    
    def parse_xml_input(self, xml_content: str) -> List[MedicationData]:
        """Parse XML input and extract medication data"""
        try:
            # Remove the outer <XML> wrapper if present
            if xml_content.strip().startswith('<XML>'):
                xml_content = xml_content.replace('<XML>', '').replace('</XML>', '').strip()
            
            root = ET.fromstring(xml_content)
            
            medications = []
            for medication_elem in root.findall('.//Medication'):
                medication = MedicationData(
                    sub_id=medication_elem.find('sub_id').text if medication_elem.find('sub_id') is not None else '',
                    substance=medication_elem.find('substance').text if medication_elem.find('substance') is not None else '',
                    advice=medication_elem.find('advice').text if medication_elem.find('advice') is not None else '',
                    ref_1_id=medication_elem.find('ref_1_id').text if medication_elem.find('ref_1_id') is not None else None,
                    ref_1_name=medication_elem.find('ref_1_name').text if medication_elem.find('ref_1_name') is not None else None,
                    ref_1_advice=medication_elem.find('ref_1_advice').text if medication_elem.find('ref_1_advice') is not None else None
                )
                medications.append(medication)
            
            return medications
            
        except ET.ParseError as e:
            print(f"❌ Error parsing XML: {e}")
            return []
        except Exception as e:
            print(f"❌ Error processing XML: {e}")
            return []
    
    def generate_xml_output(self, medications: List[MedicationData], results: Dict[str, Dict]) -> str:
        """Generate XML output with SNOMED CT and ATC codes"""
        # Create XML structure
        root = ET.Element('XML-File')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        
        for medication in medications:
            medication_elem = ET.SubElement(root, 'Medication')
            
            # Get SNOMED CT and ATC codes
            substance_name = medication.substance
            result = results.get(substance_name, {})
            
            snomed_ct = result.get('conceptId', 'SNOMED CT not found') if result.get('found') else 'SNOMED CT not found'
            atc_code = self.get_atc_codes_from_felleskatalogen(substance_name)
            
            # Add SNOMED CT and ATC codes
            snomed_elem = ET.SubElement(medication_elem, 'snomed_ct')
            snomed_elem.text = snomed_ct
            
            atc_elem = ET.SubElement(medication_elem, 'atc')
            atc_elem.text = atc_code
            
            # Add original data
            sub_id_elem = ET.SubElement(medication_elem, 'sub_id')
            sub_id_elem.text = medication.sub_id
            
            substance_elem = ET.SubElement(medication_elem, 'substance')
            substance_elem.text = medication.substance
            
            advice_elem = ET.SubElement(medication_elem, 'advice')
            advice_elem.text = medication.advice
            
            # Add reference data if present
            if medication.ref_1_id:
                ref_1_id_elem = ET.SubElement(medication_elem, 'ref_1_id')
                ref_1_id_elem.text = medication.ref_1_id
            
            if medication.ref_1_name:
                ref_1_name_elem = ET.SubElement(medication_elem, 'ref_1_name')
                ref_1_name_elem.text = medication.ref_1_name
            
            if medication.ref_1_advice:
                ref_1_advice_elem = ET.SubElement(medication_elem, 'ref_1_advice')
                ref_1_advice_elem.text = medication.ref_1_advice
        
        # Convert to string with proper formatting
        xml_str = ET.tostring(root, encoding='unicode', method='xml')
        
        # Format the XML with proper indentation
        formatted_xml = self._format_xml(xml_str)
        
        # Add XML declaration
        final_xml = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n{formatted_xml}'
        
        return final_xml
    
    def _format_xml(self, xml_str: str) -> str:
        """Format XML string with proper indentation"""
        try:
            # Parse and reformat with indentation
            root = ET.fromstring(xml_str)
            
            # Create a function to recursively format elements
            def format_element(elem, level=0):
                indent = '\t' * level
                result = f'{indent}<{elem.tag}'
                
                # Add attributes
                for key, value in elem.attrib.items():
                    result += f' {key}="{value}"'
                
                if elem.text and elem.text.strip():
                    result += f'>{elem.text}</{elem.tag}>'
                elif len(elem) > 0:
                    result += '>\n'
                    for child in elem:
                        result += format_element(child, level + 1) + '\n'
                    result += f'{indent}</{elem.tag}>'
                else:
                    result += f'/>'
                
                return result
            
            formatted = format_element(root)
            return formatted
            
        except Exception as e:
            print(f"Warning: Could not format XML properly: {e}")
            return xml_str
    
    def generate_output_filename(self, input_filename: str) -> str:
        """Generates an output filename with a running number."""
        # Extract base filename without path
        base_name = input_filename.split('/')[-1]
        
        # Split name and extension
        if '.' in base_name:
            name, ext = base_name.rsplit('.', 1)
        else:
            name = base_name
            ext = 'xml'
        
        # Get next output number
        output_number = self._get_next_output_number(input_filename)
        
        # Create output filename
        output_name = f"Output/output_{output_number:02d}_{name}.{ext}"
        return output_name
    
    def _get_next_output_number(self, input_filename: str) -> int:
        """Gets the next available output number for the current input file."""
        counter_file = "Output/.output_counter"
        
        try:
            # Ensure Output directory exists
            import os
            os.makedirs("Output", exist_ok=True)
            
            # Extract base filename without path and extension
            base_name = input_filename.split('/')[-1]
            if '.' in base_name:
                name, _ = base_name.rsplit('.', 1)
            else:
                name = base_name
            
            # Read current counter from file
            if os.path.exists(counter_file):
                with open(counter_file, 'r') as f:
                    counter_data = f.read().strip()
                    if counter_data:
                        try:
                            last_filename, last_number = counter_data.split(':', 1)
                            last_number = int(last_number)
                        except ValueError:
                            last_filename = ""
                            last_number = 0
                    else:
                        last_filename = ""
                        last_number = 0
            else:
                last_filename = ""
                last_number = 0
            
            # Reset counter to 1 if filename changed
            if last_filename != name:
                next_number = 1
            else:
                next_number = last_number + 1
            
            # Save updated counter with current filename
            with open(counter_file, 'w') as f:
                f.write(f"{name}:{next_number}")
            
            return next_number
            
        except Exception as e:
            print(f"Warning: Could not manage output counter: {e}")
            # Fallback to session-based counter
            if not hasattr(self, '_output_number_counter'):
                self._output_number_counter = 0
            self._output_number_counter += 1
            return self._output_number_counter
    
    def map_medications_from_xml(self, xml_content: str) -> Tuple[List[MedicationData], Dict[str, Dict]]:
        """Map medications from XML input to medicinal products"""
        # Parse XML input
        medications = self.parse_xml_input(xml_content)
        
        if not medications:
            print("❌ No medications found in XML input")
            return [], {}
        
        print(f"🔍 Found {len(medications)} medications in XML input")
        print("=" * 80)
        
        # Map each substance to medicinal products
        results = {}
        for medication in medications:
            substance_name = medication.substance
            print(f"\n📋 Mapping: {substance_name}")
            
            medicinal_product = self.find_medicinal_product_for_substance(substance_name)
            
            if medicinal_product:
                results[substance_name] = {
                    'found': True,
                    'conceptId': medicinal_product.conceptId,
                    'fsn': medicinal_product.fsn,
                    'pt': medicinal_product.pt,
                    'status': medicinal_product.definitionStatus,
                    'effectiveTime': medicinal_product.effectiveTime,
                    'match_type': self._classify_match(medicinal_product, substance_name)
                }
                
                print(f"  ✅ Found: {medicinal_product.conceptId}")
                print(f"     FSN: {medicinal_product.fsn}")
                print(f"     PT: {medicinal_product.pt}")
                print(f"     Match Type: {results[substance_name]['match_type']}")
            else:
                results[substance_name] = {
                    'found': False,
                    'conceptId': None,
                    'fsn': None,
                    'pt': None,
                    'status': None,
                    'effectiveTime': None,
                    'match_type': 'Not found'
                }
                
                print(f"  ❌ Not found")
            
            # Look up ATC codes
            print(f"  🔍 Looking up ATC codes...")
            atc_codes = self.get_atc_codes_from_felleskatalogen(substance_name)
            print(f"     ATC: {atc_codes}")
        
        return medications, results
    
    def _classify_match(self, product: MedicinalProduct, substance_name: str) -> str:
        """Classify the type of match"""
        if self._is_exact_only_match(product, substance_name):
            return "Exact 'Product containing only' match"
        else:
            score = self._calculate_match_score(product, substance_name)
            if score >= 90:
                return "High priority match"
            elif score >= 50:
                return "Medium priority match"
            else:
                return "Low priority match"
    
    def print_summary(self, results: Dict[str, Dict]):
        """Print a summary of the mapping results"""
        print("\n" + "=" * 80)
        print("XML MAPPING SUMMARY")
        print("=" * 80)
        
        found_count = sum(1 for result in results.values() if result['found'])
        total_count = len(results)
        
        print(f"📊 Total substances: {total_count}")
        print(f"✅ Found: {found_count}")
        print(f"❌ Not found: {total_count - found_count}")
        print(f"📈 Success rate: {(found_count/total_count)*100:.1f}%")
        
        if found_count > 0:
            print(f"\n🎯 Found Concept IDs:")
            for substance_name, result in results.items():
                if result['found']:
                    print(f"   {substance_name}: {result['conceptId']} ({result['match_type']})")
        
        if total_count - found_count > 0:
            print(f"\n❌ Not found:")
            for substance_name, result in results.items():
                if not result['found']:
                    print(f"   {substance_name}")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python improved_medicinal_product_mapper.py --xml <xml_file>")
        print("   OR: python improved_medicinal_product_mapper.py --xml-content <xml_content>")
        print("   OR: python improved_medicinal_product_mapper.py --test (uses Testsett/test_medications.xml)")
        sys.exit(1)
    
    mapper = XMLMedicinalProductMapper()
    
    if sys.argv[1] == "--xml":
        if len(sys.argv) < 3:
            print("❌ Please provide an XML filename after --xml")
            sys.exit(1)
        
        filename = sys.argv[2]
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                xml_content = file.read()
        except FileNotFoundError:
            print(f"❌ File '{filename}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            sys.exit(1)
        
        print(f"📁 Loaded XML from '{filename}'")
        
    elif sys.argv[1] == "--xml-content":
        if len(sys.argv) < 3:
            print("❌ Please provide XML content after --xml-content")
            sys.exit(1)
        
        xml_content = sys.argv[2]
        filename = "xml_content"  # Default name for direct content
        print(f"🔍 Processing XML content from command line")
    
    elif sys.argv[1] == "--test":
        # Use the default test file in Testsett folder
        filename = "Testsett/testsett.xml"
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                xml_content = file.read()
        except FileNotFoundError:
            print(f"❌ Test file '{filename}' not found. Please ensure testsett.xml exists in the Testsett folder.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error reading test file: {e}")
            sys.exit(1)
        
        print(f"🧪 Using test file: '{filename}'")
    
    else:
        print("❌ Invalid option. Use --xml, --xml-content, or --test")
        sys.exit(1)
    
    # Map medications from XML
    medications, results = mapper.map_medications_from_xml(xml_content)
    
    if not medications:
        print("❌ No medications to process")
        sys.exit(1)
    
    # Print summary
    mapper.print_summary(results)
    
    # Generate XML output
    output_xml = mapper.generate_xml_output(medications, results)
    
    # Generate output filename with running number
    output_filename = mapper.generate_output_filename(filename)
    
    # Ensure Output directory exists
    import os
    os.makedirs("Output", exist_ok=True)
    
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(output_xml)
    
    print(f"\n💾 XML output saved to: '{output_filename}'")
    print(f"\n🎉 XML mapping complete! Check the generated XML file for your results.")


if __name__ == "__main__":
    main()
