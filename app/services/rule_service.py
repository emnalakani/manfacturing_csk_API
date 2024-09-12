import json

class RuleTemplate:
    def __init__(self, expression: str, id: int = None):
        self.id = id
        self.expression = expression

    def __str__(self):
        return self.expression

class MCSK:
    def __init__(self, statement: str):
        self.statement = statement

    def __str__(self):
        return self.statement

class ConcreteRule:
    def __init__(self, expression: str, id: int = None):
        self.id = id
        self.expression = expression

    def __str__(self):
        return self.expression

RT1 = RuleTemplate("∀x (product(x) → ∃y (process(y) ∧ isOutputOf(x, y)))",1)
RT2 = RuleTemplate("∀x (process(x) → ∃y (machine(y) ∧ participatesAtSomeTime(y, x)))",2)
RT3 = RuleTemplate("∀x (process(x) → ∃y (process(y) ∧ precedes(x, y)))",3)
RT4 = RuleTemplate("∀x (product(x) → ∃y (material(y) ∧ partOf(y, x)))", 4)
RT5 = RuleTemplate("∀x (assembly(x) → ∃y (assemblyProcess(y) ∧ isOutputOf(x, y)))", 5)
RT6 = RuleTemplate("∀x (assembly(x) → ∃y (component(y) ∧ isInputOf(y, x)))", 6)
RT7 = RuleTemplate("∀x (assembly(x) → ∃y,z (picking(y) ∧ fixing(z) ∧ partOf(y, x) ∧ partOf(z, x)))", 7)
RT8 = RuleTemplate("∀x,y (component1(x) ∧ component2(y) ∧ process(p1) ∧ isOutputOf(y, p1) ∧ process(p2) ∧ isOutputOf(x, p2))", 8)

def determine_rule_template(mcsk: MCSK) -> RuleTemplate:
    if "needs to be performed for making" in mcsk.statement:
        print(f"Using RT1 for statement: {mcsk.statement}")
        return RT1
    elif "needs to be used in the " in mcsk.statement:
        print(f"Using RT2 for statement: {mcsk.statement}")
        return RT2
    elif "needs to be performed before" in mcsk.statement:
        print(f"Using RT3 for statement: {mcsk.statement}")
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

    CR_expression = RT.expression

    print(MCSK.statement)

    if "needs to be performed for making" in MCSK.statement:
        process_name = ' '.join(words[:words.index("needs")])
        product_name = ' '.join(words[words.index("making") + 2:]).rstrip('.')
        CR_expression = CR_expression.replace("process(y)", f"{process_name}(y)")
        CR_expression = CR_expression.replace("product(x)", f"{product_name}(x)")

    elif "needs to be used in the " in MCSK.statement:
        tool_name = ' '.join(words[:words.index("needs")])
        process_name = ' '.join(words[words.index("the") + 1:]).rstrip('.')
        CR_expression = CR_expression.replace("machine(y)", f"{tool_name}(y)")
        CR_expression = CR_expression.replace("process(x)", f"{process_name}(x)")

    elif "needs to be performed before" in MCSK.statement:
        preceding_process = ' '.join(words[:words.index("needs")])
        succeeding_process = ' '.join(words[words.index("before") + 1:]).rstrip('.')
        CR_expression = CR_expression.replace("process(x)", f"{preceding_process}(x)")
        CR_expression = CR_expression.replace("process(y)", f"{succeeding_process}(y)")

    # Handle RT4: "X is made of Y."
    elif "made of" in MCSK.statement:
        product_name = words[1]
        material_name = ' '.join(words[-3:]).replace('is ', '').replace('made of ', '').rstrip('.')
        CR_expression = RT4.expression.replace("product(x)", f"{product_name}(x)")
        CR_expression = CR_expression.replace("material(y)", f"{material_name}(y)")
        CR_expression = CR_expression.replace("ispartOf(y, x)", "ispartOf(y, x)")

    # Handle RT5: "Lego assembly is the output of lego assembly process."
    elif "is output of" in MCSK.statement:
        assembly_name = words[0]
        assembly_process_name = ' '.join(words[-2:]).replace('is ', '').replace('output of ', '').rstrip('.')
        CR_expression = RT5.expression.replace("assembly(x)", f"{assembly_name}(x)")
        CR_expression = CR_expression.replace("assemblyProcess(y)", f"{assembly_process_name}(y)")
        CR_expression = CR_expression.replace("isOutputOf(y, x)", "isOutputOf(x, y)")

    # Handle RT6: "Lego is the input of lego assembly."
    elif "is the input of" in MCSK.statement:
        split_index = words.index("is")
        assembly_name = ' '.join(words[split_index + 4:]).replace('is ', '').replace('the input of ', '').rstrip('.')
        component_name = ' '.join(words[:split_index]).rstrip('.')
        CR_expression = RT6.expression.replace("assembly(x)", f"{assembly_name}(x)")
        CR_expression = CR_expression.replace("component(y)", f"{component_name}(y)")
        CR_expression = CR_expression.replace("isInputOf(y, x)", "isInputOf(y, x)")

    # Handle RT7: "Lego assembly includes process1 and process2."
    elif "includes" in MCSK.statement:
        assembly_name = words[0]
        process_names = words[2:]
        process1_name = process_names[0]
        process2_name = process_names[2]
        CR_expression = RT7.expression.replace("assembly(x)", f"{assembly_name}(x)")
        CR_expression = CR_expression.replace("picking(y)", f"{process1_name}(y)")
        CR_expression = CR_expression.replace("fixing(z)", f"{process2_name}(z)")
        CR_expression = CR_expression.replace("partOf(y, x)", "partOf(y, x)")
        CR_expression = CR_expression.replace("partOf(z, x)", "partOf(z, x)")

    # Handle RT8: "Component1 X is produced by process Y and Component2 Z is produced by process W."
    elif "is produced by" in MCSK.statement:
        parts = MCSK.statement.split(" and ")
        component1_part = parts[0].split(" is produced by ")
        component2_part = parts[1].split(" is produced by ")
        component1_name = component1_part[0].strip()
        process1_name = component1_part[1].strip()
        component2_name = component2_part[0].strip()
        process2_name = component2_part[1].strip()
        CR_expression = RT8.expression.replace("component1(x)", f"{component1_name}(x)")
        CR_expression = CR_expression.replace("component2(y)", f"{component2_name}(y)")
        CR_expression = CR_expression.replace("process(p1)", f"{process1_name}(p1)")
        CR_expression = CR_expression.replace("isOutputOf(y, p1)", "isOutputOf(y, p1)")
        CR_expression = CR_expression.replace("process(p2)", f"{process2_name}(p2)")
        CR_expression = CR_expression.replace("isOutputOf(x, p2)", "isOutputOf(x, p2)")

    else:
        raise ValueError(f"Unknown MCSK format for statement: {MCSK.statement}")

    return ConcreteRule(CR_expression, RT.id)


def generate_concrete_rule(mcsk_input: str) -> ConcreteRule:
    mcsk = MCSK(mcsk_input)
    rt = determine_rule_template(mcsk)
    return SpecializeRule(rt, mcsk)

def generate_sparql_query(concrete_rule: ConcreteRule) -> str:
    expression = concrete_rule.expression
    id = concrete_rule.id
    sparql_query = ""

    if "isOutputOf" in expression and id == 1:
        # Extracting product and process names from the expression for RT1
        product_name, process_name = expression.split("(")[1].split(")")[0], expression.split("(")[3].split(")")[0]

        product_name_formatted = product_name.replace(' ', '_')
        process_name_formatted = process_name.replace(' ', '_')

        sparql_query = f"""
                IINSERT {{
            ?{product_name_formatted} rdf:type {process_name_formatted} .
            <http://www.MCSKG.enit.fr/{product_name_formatted}> <https://spec.industrialontologies.org/ontology/core/Core/isOutputOf> ?{process_name_formatted} .
            }}
            WHERE {{
            ?{product_name_formatted} rdf:type <http://www.MCSKG.enit.fr/{product_name_formatted}> .
            BIND(URI(CONCAT("http://www.MCSKG.enit.fr/{process_name_formatted}_", STRUUID())) AS ?{process_name_formatted})
                }}
        """

        # product_name = expression.split("(")[1].split(")")[0]
        # process_name = expression.split("(")[3].split(")")[0]
        # product_name_formatted = product_name.replace(' ', '_')
        # process_name_formatted = process_name.replace(' ', '_')
        # sparql_query = f"""
        # INSERT {{
        #   ?y rdf:type <http://www.mcskg.enit.fr/{process_name_formatted}> .
        #   ?x <https://spec.industrialontologies.org/ontology/core/Core/isOutputOf> ?y .
        # }}
        # WHERE {{
        #   ?x rdf:type <http://www.mcskg.enit.fr/{product_name_formatted}> .
        #   BIND(URI(CONCAT("http://www.mcskg.enit.fr/{process_name_formatted}_", STRUUID())) AS ?y)
        # }}
        # """

    elif "precedes" in expression:        
        preceding_process, succeeding_process = expression.split("(")[1].split(")")[0], expression.split("(")[3].split(")")[0]

        preceding_process_formatted = preceding_process.replace(' ', '_')
        succeeding_process_formatted = succeeding_process.replace(' ', '_')

        sparql_query = f"""
        INSERT {{
            ?{preceding_process_formatted} rdf:type <http://purl.obolibrary.org/obo/BFO_0000015> .
            <http://www.MCSKG.enit.fr/{preceding_process_formatted}> <http://purl.obolibrary.org/obo/BFO_0000063> ?{succeeding_process_formatted} .
        }}
        WHERE {{
            ?{preceding_process_formatted} rdf:type <http://purl.obolibrary.org/obo/BFO_0000015> .
            BIND(URI(CONCAT("http://www.MCSKG.enit.fr/{succeeding_process_formatted}_", STRUUID())) AS ?{succeeding_process_formatted})
        }}
        """
        # preceding_process = expression.split("(")[1].split(")")[0]
        # succeeding_process = expression.split("(")[3].split(")")[0]
        # preceding_process_formatted = preceding_process.replace(' ', '_')
        # succeeding_process_formatted = succeeding_process.replace(' ', '_')
        # sparql_query = f"""
        # INSERT {{
        # ?y rdf:type <http://www.mcskg.enit.fr/{succeeding_process_formatted}> .
        # ?y <http://purl.obolibrary.org/obo/BFO_0000063> ?x .
        # }}
        #  WHERE {{
        # ?x rdf:type <http://www.mcskg.enit.fr/{preceding_process_formatted}>.
        # BIND(URI(CONCAT("http://www.mcskg.enit.fr/{succeeding_process_formatted}_", STRUUID())) AS ?y)
        # }}
        # """

    elif "participatesAtSomeTime" in expression:
        tool_name, process_name = expression.split("(")[3].split(")")[0], expression.split("(")[1].split(")")[0]

        process_name_formatted = process_name.replace(' ', '_')
        tool_name_formatted = tool_name.replace(' ', '_')
        sparql_query = f"""
        INSERT DATA {{
            ?{process_name_formatted} rdf:type <http://purl.obolibrary.org/obo/BFO_0000015> .
            <http://www.MCSKG.enit.fr/{tool_name_formatted}> <http://purl.obolibrary.org/obo/BFO_0000056> ?{process_name_formatted} .
        }}
        WHERE {{
            BIND(URI(CONCAT("http://www.MCSKG.enit.fr/{tool_name_formatted}_", STRUUID())) AS ?{tool_name_formatted})
        }}
        """

    elif "ispartOf" in expression:
        product_name = expression.split("(")[1].split(")")[0]
        material_name = expression.split("(")[3].split(")")[0]
        product_name_formatted = product_name.replace(' ', '_')
        material_name_formatted = material_name.replace(' ', '_')
        sparql_query = f"""
        INSERT {{
            ?y rdf:type <http://www.mcskg.enit.fr/{material_name_formatted}> .
            ?y <https://spec.industrialontologies.org/ontology/core/Core/isOutputOf> ?x .
        }}
        WHERE {{
            ?x rdf:type <http://www.mcskg.enit.fr/{product_name_formatted}> .
            BIND(URI(CONCAT("http://www.mcskg.enit.fr/{material_name_formatted}_", STRUUID())) AS ?y)
        }}
        """

    elif "isOutputOf" in expression and id == 5:
        assembly_name = expression.split("(")[1].split(")")[0]
        assembly_process_name = expression.split("(")[2].split(")")[0]
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
        assembly_name_formatted = assembly_name.replace(' ', '_')
        process1_name_formatted = process1_name.replace(' ', '_')
        process2_name_formatted = process2_name.replace(' ', '_')
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
        component1_name = expression.split("(")[1].split(")")[0]
        component2_name = expression.split("(")[2].split("∧ ")[1]
        process1_name = expression.split("(")[3].split("∧ ")[1]
        process2_name = expression.split("(")[5].split("∧ ")[1]
        component1_name_formatted = component1_name.replace(' ', '_')
        component2_name_formatted = component2_name.replace(' ', '_')
        process1_name_formatted = process1_name.replace(' ', '_')
        process2_name_formatted = process2_name.replace(' ', '_')
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

def generate_datalog_rule(concrete_rule: ConcreteRule) -> str:
    expression = concrete_rule.expression
    datalog_rule = ""

    print(expression)

    if "isOutputOf" in expression:
        product_name = expression.split("(")[1].split(")")[0]
        process_name = expression.split("(")[3].split(")")[0]

        datalog_rule = f"""
        [?{product_name}, BFO:isOutputOf, ?{process_name}] :-
            [?{process_name}, a, BFO:Process],
            [?{product_name}, a, BFO:Product].
        """

    elif "precedes" in expression:
        preceding_process = expression.split("(")[1].split(")")[0]
        succeeding_process = expression.split("(")[3].split(")")[0]

        datalog_rule = f"""
        [?{preceding_process}, BFO:Precedes, ?{succeeding_process}] :-
            [?{preceding_process}, a, BFO:Process],
            [?{succeeding_process}, a, BFO:Process].
        """

    elif "participatesAtSomeTime" in expression:
        process_name = expression.split("(")[1].split(")")[0]
        tool_name = expression.split("(")[3].split(")")[0]

        datalog_rule = f"""
        [?{tool_name}, 'BFO:participatesAtSomeTime', ?{process_name}] :-
            [?{process_name}, a, BFO:Process],
            [?{tool_name}, a, IOF:Machine].
        """
    else:
        raise ValueError("Unknown Rule Type in Concrete Rule!")

    return datalog_rule
