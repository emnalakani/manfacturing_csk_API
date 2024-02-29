class RuleTemplate:
    def __init__(self, expression: str, id: int = None):
        """Initialize the RuleTemplate class with an expression.

        Args:
        expression (str): A logical expression containing placeholders.
        """
        self.id = id
        self.expression = expression

    def __str__(self):
        return self.expression

#MCSK Class: Represents a Manufacturing Common Sense Knowledge statement, which provides specific knowledge about manufacturing
class MCSK:
    def __init__(self, statement: str):
        """Initialize the MCSK class with a statement.

        Args:
        statement (str): A statement that provides specific knowledge about manufacturing.
        """
        self.statement = statement

    def __str__(self):
        return self.statement

#ConcreteRule Class: Represents a concrete rule derived from a rule template by replacing its placeholders with specific classes/instances.
class ConcreteRule:
    def __init__(self, expression: str, id: int = None):
        """Initialize the ConcreteRule class with an expression.

        Args:
        expression (str): A logical expression that's the result of substituting placeholders in a RuleTemplate with information from an MCSK.
        """
        self.id = id
        self.expression = expression

    def __str__(self):
        return self.expression

RT1 = RuleTemplate("∀x (product(x) → ∃y (process(y) ∧ isOutputOf(x, y)))", 1)
RT2 = RuleTemplate("∀x (process(x) → ∃y (process(y) ∧ precedes(x, y)))", 2)
RT3 = RuleTemplate("∀x (process(x) → ∃y (machine(y) ∧ participatesAtSomeTime(y, x)))", 3)
RT4 = RuleTemplate("∀x (product(x) → ∃y (material(y) ∧ partOf(y, x)))", 4)
RT5 = RuleTemplate("∀x (assembly(x) → ∃y (assemblyProcess(y) ∧ isOutputOf(x, y)))", 5)
RT6 = RuleTemplate("∀x (assembly(x) → ∃y (component(y) ∧ isInputOf(y, x)))" ,6)
RT7 = RuleTemplate("∀x (assembly(x) → ∃y,z (picking(y) ∧ fixing(z) ∧ partOf(y, x) ∧ partOf(z, x)))", 7)
RT8 = RuleTemplate("∀x,y (component1(x) ∧ component2(y) ∧ process(p1) ∧ isOutputOf(y, p1) ∧ process(p2) ∧ isOutputOf(x, p2))", 8)
def determine_rule_template(mcsk: MCSK) -> RuleTemplate:
    if "result" in mcsk.statement:
        return RT1
    elif "After" in mcsk.statement:
        return RT2
    elif "involves" in mcsk.statement:
        return RT3
    elif "made of" in mcsk.statement:
        return RT4
    elif "is output of" in mcsk.statement:
        return RT5
    elif "is the input of" in mcsk.statement:
        return RT6
    elif "includes" in mcsk.statement:
        return RT7
    elif "is produced by" in mcsk.statement:
        return RT8
    else:
        raise ValueError("Unknown MCSK format!")


def SpecializeRule(RT: RuleTemplate, MCSK: MCSK) -> ConcreteRule:
    words = MCSK.statement.split()

    # Handle RT1: "The result of X is a Y." #The result of painting is a painted object
    if "result" in MCSK.statement:
        words = MCSK.statement.split()
        process_name = words[3]
        product_name = ' '.join(words[-3:]).replace('a ', '').replace('an ', '').replace('is ', '').rstrip('.')
        CR_expression = RT.expression.replace("product(x)", f"{product_name}(x)")
        CR_expression = CR_expression.replace("process(y)", f"{process_name}(y)")
        CR_expression = CR_expression.replace("isOutputOf(x, y)", "isOutputOf(x, y)")

    # Handle RT2: "X process After Y process." #After painting you should dry
    elif "After" in MCSK.statement:
        preceding_process = words[1]  # In the given example, this should be "painting"
        succeeding_process = words[4]  # In the given example, this should be "dry"
        CR_expression = RT.expression.replace("process(x)", f"{preceding_process}(x)")
        CR_expression = CR_expression.replace("process(y)", f"{succeeding_process}(y)")
        CR_expression = CR_expression.replace("precedes(y, x)", "precedes(y, x)")

    # Handle RT3: "X process involves Y machine." #The drying process involves a dryer machine
    else:
        process_name = words[1]  # This will extract "process" from the MCSK statement
        machine_name = ' '.join(words[-2:])  # This will extract "machine" from the MCSK statement
        machine_name = machine_name.replace('a ', '').replace('an ', '').rstrip('.')
        CR_expression = RT.expression.replace("process(x)", f"{process_name}(x)")
        CR_expression = CR_expression.replace("machine(y)", f"{machine_name}(y)")
        CR_expression = CR_expression.replace("participatesAtSomeTime(y, x)", "participatesAtSomeTime(y, x)")

    # Handle RT4: "X is made of Y." # e.g., The lego structure is made of lego Blocks
    if "made of" in MCSK.statement:
        words = MCSK.statement.split()
        product_name = words[1]  # Assuming the product name is the first word
        material_name = ' '.join(words[-3:]).replace('is ', '').replace('made of ', '').rstrip('.')
        CR_expression = RT4.expression.replace("product(x)", f"{product_name}(x)")
        CR_expression = CR_expression.replace("material(y)", f"{material_name}(y)")
        CR_expression = CR_expression.replace("ispartOf(y, x)", "ispartOf(y, x)")

        # Handle RT5: "Lego assembly is the output of lego assembly process."
    if "is output of" in MCSK.statement:
        words = MCSK.statement.split()
        assembly_name = words[0]  # Assuming the assembly name is the first word
        assembly_process_name = ' '.join(words[-2:]).replace('is ', '').replace('output of ', '').rstrip('.')
        CR_expression = RT5.expression.replace("assembly(x)", f"{assembly_name}(x)")
        CR_expression = CR_expression.replace("assemblyProcess(y)", f"{assembly_process_name}(y)")
        CR_expression = CR_expression.replace("isOutputOf(y, x)", "isOutputOf(x, y)")

    # Handle RT6: "Lego is the input of lego assembly."
    if "is the input of" in MCSK.statement:
      words = MCSK.statement.split()
      split_index = words.index("is")  # Find the position of 'is' in the statement
      assembly_name = ' '.join(words[split_index + 4:]).replace('is ', '').replace('the input of ', '').rstrip('.')  # Everything after "is the input of"
      component_name = ' '.join(words[:split_index]).rstrip('.')  # Everything before "is the input of"

    # Debugging prints
      print(f"Extracted assembly_name: {assembly_name}")
      print(f"Extracted component_name: {component_name}")

      CR_expression = RT6.expression.replace("assembly(x)", f"{assembly_name}(x)")
      CR_expression = CR_expression.replace("component(y)", f"{component_name}(y)")
      CR_expression = CR_expression.replace("isInputOf(y, x)", "isInputOf(y, x)")
    # Handle RT7: "Lego assembly involves process1 and process2."
    if "includes" in MCSK.statement:
      words = MCSK.statement.split()
      assembly_name = words[0]  # Assuming the assembly name is the first word
      process_names = words[2:]  # Assuming processes start after 'involves'

      # Extracting two process names
      process1_name = process_names[0]
      process2_name = process_names[2]  # Assuming 'and' is in between
      # Debugging prints
      print(f"Extracted process1_name: {process1_name}")
      print(f"Extracted process2_name: {process2_name}")
      # Create the ConcreteRule expression
      CR_expression = RT7.expression.replace("assembly(x)", f"{assembly_name}(x)")
      CR_expression = CR_expression.replace("process(y)", f"{process1_name}(y)")
      CR_expression = CR_expression.replace("process(z)", f"{process2_name}(z)")
      CR_expression = CR_expression.replace("partOf(y, x)", "partOf(y, x)")
      CR_expression = CR_expression.replace("partOf(z, x)", "partOf(z, x)")
    # Handle RT8: "Component1 [Name] is produced by process [Process1] and Component2 [Name] is produced by process [Process2]."

    if "is produced by" in MCSK.statement:
      # Split the statement into two parts: one for each component and its process
      parts = MCSK.statement.split(" and ")
      component1_part = parts[0].split(" is produced by ")
      component2_part = parts[1].split(" is produced by ")

     # Extract component and process names
      component1_name = component1_part[0].strip()
      process1_name = component1_part[1].strip()
      component2_name = component2_part[0].strip()
      process2_name = component2_part[1].strip()

      # Debugging prints
      print(f"Extracted component1_name: {component1_name}")
      print(f"Extracted component2_name: {component2_name}")
      print(f"Extracted process1_name: {process1_name}")
      print(f"Extracted process2_name: {process2_name}")

       #Create the ConcreteRule expression
      CR_expression = RT8.expression.replace("component1(x)", f"{component1_name}(x)")
      CR_expression = CR_expression.replace("component2(y)", f"{component2_name}(y)")
      CR_expression = CR_expression.replace("process(p1)", f"{process1_name}(p1)")
      CR_expression = CR_expression.replace("isOutputOf(y, p1)", "isOutputOf(y, p1)")
      CR_expression = CR_expression.replace("process(p2)", f"{process2_name}(p2)")
      CR_expression = CR_expression.replace("isOutputOf(x, p2)", "isOutputOf(x, p2)")

    return ConcreteRule(CR_expression, RT.id)


def generate_concrete_rule(mcsk_input: str) -> ConcreteRule:
    mcsk = MCSK(mcsk_input)
    rt = determine_rule_template(mcsk)
    return SpecializeRule(rt, mcsk)
def generate_sparql_query(concrete_rule: ConcreteRule) -> str:
    expression = concrete_rule.expression
    id = concrete_rule.id
    sparql_query = ""

    # Example of how to parse the expression and generate a SPARQL query
    if "isOutputOf" in expression and id==1 :
        # Extracting product and process names from the expression for RT1 ∀x (painted object(x) → ∃y (painting(y) ∧ isOutputOf(x, y)))
        product_name = expression.split("(")[1].split(")")[0]
        process_name = expression.split("(")[3].split(")")[0]
         # Print statements for debugging
        print(f"Extracted product name: {product_name}")
        print(f"Extracted process name: {process_name}")

        # Correctly replacing spaces with underscores for valid IRIs
        process_name_formatted = process_name.replace(' ', '_')
        product_name_formatted = product_name.replace(' ', '_')

        sparql_query = f"""
        INSERT {{
          ?y rdf:type <http://www.mcskg.enit.fr/{process_name_formatted}> .
          ?x <https://spec.industrialontologies.org/ontology/core/Core/isOutputOf> ?y .
          }}
        WHERE {{
          ?x rdf:type <http://www.mcskg.enit.fr/{product_name_formatted}> .
          BIND(URI(CONCAT("http://www.mcskg.enit.fr/{process_name_formatted}_", STRUUID())) AS ?y)
          }}
          """
    elif "precedes" in expression:
        # Similar parsing for RT2
        preceding_process = expression.split("(")[1].split(")")[0]
        succeeding_process = expression.split("(")[3].split(")")[0]
        # Print statements for debugging
        print(f"Extracted preceding_process name: {preceding_process}")
        print(f"Extracted succeeding_process name: {succeeding_process}")

        # Correctly replacing spaces with underscores for valid IRIs
        preceding_process_formatted = preceding_process.replace(' ', '_')
        succeeding_process_formatted = succeeding_process.replace(' ', '_')

        sparql_query = f"""
        INSERT {{
        ?y rdf:type <"http://www.mcskg.enit.fr/{succeeding_process_formatted}"> .
        ?y <http://purl.obolibrary.org/obo/BFO_0000063> ?x .
        }}
         WHERE {{
        ?x rdf:type <"http://www.mcskg.enit.fr/{preceding_process_formatted}">.
        BIND(URI(CONCAT("http://www.mcskg.enit.fr/{succeeding_process_formatted}_", STRUUID())) AS ?y)
        }}
        """

    elif "participatesAtSomeTime" in expression:
        # Similar parsing for RT3
        process_name = expression.split("(")[1].split(")")[0]
        machine_name = expression.split("(")[3].split(")")[0]
        # Print statements for debugging
        print(f"Extracted process name:  {process_name}")
        print(f"Extracted machine name: {machine_name}")

        # Correctly replacing spaces with underscores for valid IRIs
        process_name_formatted = process_name.replace(' ', '_')
        machine_name_formatted = machine_name.replace(' ', '_')
        sparql_query = f"""

        INSERT {{
        ?y rdf:type <http://www.mcskg.enit.fr/{machine_name_formatted}>"> .
        ?y <http://purl.obolibrary.org/obo/BFO_0000056> ?x .
        }}
         WHERE {{
        ?x rdf:type <"http://www.mcskg.enit.fr/{process_name_formatted}">.
        BIND(URI(CONCAT("http://www.mcskg.enit.fr/{machine_name_formatted}_", STRUUID())) AS ?y)
        }}
        """

    elif "ispartOf" in expression:
        # Extracting product and material names from the expression
        product_name = expression.split("(")[1].split(")")[0]
        material_name = expression.split("(")[3].split(")")[0]
          # Print statements for debugging
        print(f"Extracted product_name:  {product_name}")
        print(f"Extracted  material_name: {material_name}")
        # Replacing spaces with underscores for valid IRIs
        product_name_formatted = product_name.replace(' ', '_')
        material_name_formatted = material_name.replace(' ', '_')

        # Constructing the SPARQL query
        sparql_query = f"""
        INSERT {{
            ?y rdf:type <http://www.mcskg.enit.fr/{material_name_formatted}> .
            ?y <https://spec.industrialontologies.org/ontology/core/Core/isOutputOf>?x .
        }}
        WHERE {{
            <?x rdf:type <http://www.mcskg.enit.fr/{product_name_formatted}> .
            BIND(URI(CONCAT("http://www.mcskg.enit.fr/{material_name_formatted}_", STRUUID())) AS ?y)
        }}
        """

    elif "isOutputOf" in expression and id == 5:
        assembly_name = expression.split("(")[1].split(")")[0]
        assembly_process_name = expression.split("(")[2].split(")")[0]
          # Print statements for debugging
        print(f"Extracted assembly_name:  {assembly_name}")
        print(f"Extracted  material_name: {assembly_process_name}")
        assembly_name_formatted = assembly_name.replace(' ', '_')
        assembly_process_name_formatted = assembly_process_name.replace(' ', '_')

        sparql_query = f"""
        INSERT {{
            ?y rdf:type <http://www.mcskg.enit.fr/{assembly_process_name_formatted}> .
            ?x <https://spec.industrialontologies.org/ontology/core/Core/isOutputOf> ?y .
        }}
        WHERE {{
          ?x  rdf:type <http://www.mcskg.enit.fr/{assembly_name_formatted}>  .
            BIND(URI(CONCAT("http://www.mcskg.enit.fr/{assembly_process_name_formatted}_", STRUUID())) AS ?y)
        }}
        """
    elif "isInputOf" in expression:
        assembly_name = expression.split("(")[1].split(")")[0]
        component_name = expression.split("(")[3].split(")")[0]
              # Print statements for debugging
        print(f"Extracted assembly_name:  {assembly_name}")
        print(f"Extracted  component_name: {component_name}")
        assembly_name_formatted = assembly_name.replace(' ', '_')
        component_name_formatted = component_name.replace(' ', '_')

        sparql_query = f"""
        INSERT {{
            ?y rdf:type <http://www.mcskg.enit.fr/{component_name_formatted}> .
            ?y <http://example.org/isInputOf> ?x .
        }}
        WHERE {{
            ?x rdf:type <http://www.mcskg.enit.fr/{assembly_name_formatted}> .
            BIND(URI(CONCAT("http://www.mcskg.enit.fr/{component_name_formatted}_", STRUUID())) AS ?y)
        }}
        """
    elif "partOf" in expression:
        assembly_name = expression.split("(")[1].split(")")[0]
        process1_name = expression.split("(")[3].split(")")[0]
        process2_name = expression.split("(")[4].split("∧ ")[1]
           # Print statements for debugging
        print( expression.split("("))
        print(f"Extracted assembly_name:  {assembly_name}")
        print(f"Extracted process1_namee: {process1_name}")
        print(f"Extracted process2_namee: {process2_name}")

        assembly_name_formatted = assembly_name.replace(' ', '_')
        process1_name_formatted = process1_name.replace(' ', '_')
        process2_name_formatted = process2_name.replace(' ', '_')

        # Print statements for debugging
        print(f"Extracted assembly_name:  {assembly_name}")
        print(f"Extracted  process1_name: {process1_name}")
        print(f"Extracted  process2_name: {process2_name}")

        sparql_query = f"""
        INSERT {{
            ?y rdf:type <http://www.mcskg.enit.fr/{process1_name_formatted}> .
            ?z rdf:type <http://www.mcskg.enit.fr/{process2_name_formatted}> .
            ?y <http://example.org/partOf> ?x.
            ?z <http://example.org/partOf> ?x.
        }}
        WHERE {{
            ?x rdf:type <http://www.mcskg.enit.fr/{assembly_name}> .
            BIND(URI(CONCAT("http://www.mcskg.enit.fr/{process1_name_formatted}_", STRUUID())) AS ?y)
            BIND(URI(CONCAT("http://www.mcskg.enit.fr/{process2_name_formatted}_", STRUUID())) AS ?z)
        }}
        """

    elif "isOutputOf" in expression and id == 8:
      # Print statements for debugging
        component1_name= expression.split("(")[1].split(")")[0]
        component2_name = expression.split("(")[2].split("∧ ")[1]
        process1_name = expression.split("(")[3].split("∧ ")[1]
        process2_name = expression.split("(")[5].split("∧ ")[1]

        print( expression.split("("))
        component1_name_formatted = component1_name.replace(' ', '_')
        component2_name_formatted = component2_name.replace(' ', '_')
        process1_name_formatted = process1_name.replace(' ', '_')
        process2_name_formatted = process2_name.replace(' ', '_')


        # Print statements for debugging
        print(f"Extracted component1_name:  {component1_name_formatted }")
        print(f"Extracted component2_name:  {component2_name_formatted }")
        print(f"Extracted  process1_name: {process1_name_formatted}")
        print(f"Extracted  process2_name: {process2_name_formatted}")

        sparql_query = f"""
        INSERT {{
            ?p1 rdf:type <http://www.mcskg.enit.fr/{process1_name_formatted}> .
            ?p2 rdf:type <http://www.mcskg.enit.fr/{process2_name_formatted}> .
            ?y rdf:type <http://www.mcskg.enit.fr/{component2_name_formatted}> .
            ?x rdf:type <http://www.mcskg.enit.fr/{component1_name_formatted}> .
            ?y <http://example.org/isOutputOf> ?p1 .
            ?x <http://example.org/isOutputOf> ?p2 .
        }}
        WHERE {{
            BIND(URI(CONCAT("http://www.mcskg.enit.fr/{process1_name_formatted}_", STRUUID())) AS ?p1)
            BIND(URI(CONCAT("http://www.mcskg.enit.fr/{process2_name_formatted}_", STRUUID())) AS ?p2)
            BIND(URI(CONCAT("http://www.mcskg.enit.fr/{component2_name_formatted}_", STRUUID())) AS ?y)
            BIND(URI(CONCAT("http://www.mcskg.enit.fr/{component1_name_formatted}_", STRUUID())) AS ?x1)
        }}
        """

    else:
        raise ValueError("Unknown Rule Type in Concrete Rule!")

    return sparql_query