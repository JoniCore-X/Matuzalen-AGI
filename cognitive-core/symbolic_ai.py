"""
Módulo de IA Simbólica (Lógica/Símbolos/GOFAI)
Implementa razonamiento lógico formal, manipulación de símbolos y sistemas expertos.
"""

from typing import List, Dict, Any, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
from abc import ABC, abstractmethod


class LogicalOperator(Enum):
    """Operadores lógicos"""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    IMPLIES = "IMPLIES"
    IFF = "IFF"
    FORALL = "FORALL"
    EXISTS = "EXISTS"


class SymbolType(Enum):
    """Tipos de símbolos"""
    CONSTANT = "constant"
    VARIABLE = "variable"
    PREDICATE = "predicate"
    FUNCTION = "function"
    ATOM = "atom"


@dataclass
class Symbol:
    """Representa un símbolo lógico"""
    name: str
    symbol_type: SymbolType
    arity: int = 0  # Para predicados y funciones
    value: Optional[Any] = None


@dataclass
class LogicalExpression:
    """Representa una expresión lógica"""
    operator: Optional[LogicalOperator]
    operands: List['LogicalExpression']
    symbol: Optional[Symbol] = None

    def __str__(self) -> str:
        if self.symbol:
            return self.symbol.name
        elif self.operator:
            if self.operator == LogicalOperator.NOT:
                return f"NOT({self.operands[0]})"
            elif self.operator == LogicalOperator.IMPLIES:
                return f"({self.operands[0]} => {self.operands[1]})"
            elif self.operator == LogicalOperator.IFF:
                return f"({self.operands[0]} <=> {self.operands[1]})"
            elif self.operator == LogicalOperator.FORALL:
                return f"FORALL {self.operands[0]}: {self.operands[1]}"
            elif self.operator == LogicalOperator.EXISTS:
                return f"EXISTS {self.operands[0]}: {self.operands[1]}"
            else:
                op_str = f" {self.operator.value} "
                return f"({op_str.join(str(op) for op in self.operands)})"
        return ""


@dataclass
class Rule:
    """Regla de inferencia"""
    name: str
    premises: List[LogicalExpression]
    conclusion: LogicalExpression
    confidence: float = 1.0


@dataclass
class Fact:
    """Hecho en la base de conocimiento"""
    expression: LogicalExpression
    certainty: float = 1.0
    source: str = "user"


class SymbolicReasoner:
    """Motor de razonamiento simbólico"""

    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}
        self.facts: List[Fact] = []
        self.rules: List[Rule] = []
        self.inference_trace: List[Dict[str, Any]] = []

    def add_symbol(self, name: str, symbol_type: SymbolType, arity: int = 0, value: Any = None) -> None:
        """Agrega un símbolo al sistema"""
        self.symbols[name] = Symbol(name=name, symbol_type=symbol_type, arity=arity, value=value)

    def add_fact(self, expression: LogicalExpression, certainty: float = 1.0, source: str = "user") -> None:
        """Agrega un hecho a la base de conocimiento"""
        self.facts.append(Fact(expression=expression, certainty=certainty, source=source))

    def add_rule(self, name: str, premises: List[LogicalExpression],
                 conclusion: LogicalExpression, confidence: float = 1.0) -> None:
        """Agrega una regla de inferencia"""
        self.rules.append(Rule(name=name, premises=premises, conclusion=conclusion, confidence=confidence))

    def parse_expression(self, expression_str: str) -> LogicalExpression:
        """Parsea una expresión lógica desde string"""
        # Parser simplificado para expresiones lógicas
        expression_str = expression_str.strip()

        # Caso simple: átomo
        if not any(op in expression_str for op in ["AND", "OR", "NOT", "=>", "<=>"]):
            if expression_str in self.symbols:
                return LogicalExpression(symbol=self.symbols[expression_str])
            else:
                # Crear símbolo automáticamente
                self.add_symbol(expression_str, SymbolType.ATOM)
                return LogicalExpression(symbol=self.symbols[expression_str])

        # Caso: NOT
        if expression_str.startswith("NOT(") and expression_str.endswith(")"):
            inner = expression_str[4:-1]
            return LogicalExpression(
                operator=LogicalOperator.NOT,
                operands=[self.parse_expression(inner)]
            )

        # Caso: AND/OR
        for op in ["AND", "OR"]:
            if f" {op} " in expression_str:
                parts = expression_str.split(f" {op} ")
                operands = [self.parse_expression(part.strip()) for part in parts]
                return LogicalExpression(
                    operator=LogicalOperator[op],
                    operands=operands
                )

        # Caso: IMPLIES
        if " => " in expression_str:
            parts = expression_str.split(" => ")
            return LogicalExpression(
                operator=LogicalOperator.IMPLIES,
                operands=[self.parse_expression(parts[0].strip()), self.parse_expression(parts[1].strip())]
            )

        raise ValueError(f"Cannot parse expression: {expression_str}")

    def evaluate_expression(self, expression: LogicalExpression, assignment: Dict[str, bool]) -> bool:
        """Evalúa una expresión lógica con una asignación de variables"""
        if expression.symbol:
            # Átomo
            return assignment.get(expression.symbol.name, False)

        if expression.operator == LogicalOperator.NOT:
            return not self.evaluate_expression(expression.operands[0], assignment)

        if expression.operator == LogicalOperator.AND:
            return all(self.evaluate_expression(op, assignment) for op in expression.operands)

        if expression.operator == LogicalOperator.OR:
            return any(self.evaluate_expression(op, assignment) for op in expression.operands)

        if expression.operator == LogicalOperator.IMPLIES:
            p = self.evaluate_expression(expression.operands[0], assignment)
            q = self.evaluate_expression(expression.operands[1], assignment)
            return (not p) or q

        if expression.operator == LogicalOperator.IFF:
            p = self.evaluate_expression(expression.operands[0], assignment)
            q = self.evaluate_expression(expression.operands[1], assignment)
            return p == q

        return False

    def check_contradiction(self, expression: LogicalExpression) -> bool:
        """Verifica si una expresión contradice los hechos existentes"""
        # Simplificación: verificar si existe la negación
        negation = LogicalExpression(
            operator=LogicalOperator.NOT,
            operands=[expression]
        )

        for fact in self.facts:
            if self._expressions_equal(fact.expression, negation):
                return True

        return False

    def _expressions_equal(self, expr1: LogicalExpression, expr2: LogicalExpression) -> bool:
        """Verifica si dos expresiones son iguales"""
        if expr1.symbol and expr2.symbol:
            return expr1.symbol.name == expr2.symbol.name
        if expr1.operator and expr2.operator:
            if expr1.operator != expr2.operator:
                return False
            if len(expr1.operands) != len(expr2.operands):
                return False
            return all(self._expressions_equal(o1, o2) for o1, o2 in zip(expr1.operands, expr2.operands))
        return False

    def forward_chaining(self, goal: LogicalExpression, max_steps: int = 100) -> Tuple[bool, List[Dict[str, Any]]]:
        """Encadenamiento hacia adelante para alcanzar un objetivo"""
        self.inference_trace = []
        steps = 0

        while steps < max_steps:
            steps += 1
            new_facts_added = False

            for rule in self.rules:
                # Verificar si todas las premisas se cumplen
                premises_satisfied = True
                for premise in rule.premises:
                    if not self._is_fact_true(premise):
                        premises_satisfied = False
                        break

                if premises_satisfied:
                    # Agregar conclusión como nuevo hecho
                    if not self._is_fact_true(rule.conclusion):
                        self.add_fact(rule.conclusion, certainty=rule.confidence, source=rule.name)
                        new_facts_added = True

                        self.inference_trace.append({
                            'step': steps,
                            'rule': rule.name,
                            'conclusion': str(rule.conclusion),
                            'confidence': rule.confidence
                        })

                        # Verificar si alcanzamos el objetivo
                        if self._expressions_equal(rule.conclusion, goal):
                            return True, self.inference_trace

            if not new_facts_added:
                break

        # Verificar si el objetivo ya era un hecho
        if self._is_fact_true(goal):
            return True, self.inference_trace

        return False, self.inference_trace

    def backward_chaining(self, goal: LogicalExpression, max_depth: int = 50) -> Tuple[bool, List[Dict[str, Any]]]:
        """Encadenamiento hacia atrás para probar un objetivo"""
        self.inference_trace = []
        return self._backward_chaining_recursive(goal, 0, max_depth)

    def _backward_chaining_recursive(self, goal: LogicalExpression, depth: int, max_depth: int) -> Tuple[bool, List[Dict[str, Any]]]:
        """Recursión para encadenamiento hacia atrás"""
        if depth > max_depth:
            return False, self.inference_trace

        # Verificar si el objetivo ya es un hecho
        if self._is_fact_true(goal):
            return True, self.inference_trace

        # Buscar reglas que concluyan el objetivo
        for rule in self.rules:
            if self._expressions_equal(rule.conclusion, goal):
                # Intentar probar las premisas
                all_premises_proven = True
                for premise in rule.premises:
                    proven, _ = self._backward_chaining_recursive(premise, depth + 1, max_depth)
                    if not proven:
                        all_premises_proven = False
                        break

                if all_premises_proven:
                    self.inference_trace.append({
                        'step': depth,
                        'rule': rule.name,
                        'goal': str(goal),
                        'proven': True
                    })
                    self.add_fact(goal, certainty=rule.confidence, source=rule.name)
                    return True, self.inference_trace

        return False, self.inference_trace

    def _is_fact_true(self, expression: LogicalExpression) -> bool:
        """Verifica si una expresión es un hecho verdadero"""
        for fact in self.facts:
            if self._expressions_equal(fact.expression, expression) and fact.certainty > 0.5:
                return True
        return False

    def resolution(self, clauses: List[LogicalExpression]) -> List[LogicalExpression]:
        """Algoritmo de resolución para lógica proposicional"""
        new_clauses = clauses.copy()

        for i, clause1 in enumerate(clauses):
            for j, clause2 in enumerate(clauses[i+1:], i+1):
                # Intentar resolver cláusulas
                resolvent = self._resolve_pair(clause1, clause2)
                if resolvent and not self._is_tautology(resolvent):
                    if not self._clause_exists(resolvent, new_clauses):
                        new_clauses.append(resolvent)

        return new_clauses

    def _resolve_pair(self, clause1: LogicalExpression, clause2: LogicalExpression) -> Optional[LogicalExpression]:
        """Resuelve un par de cláusulas"""
        # Implementación simplificada de resolución
        if (clause1.operator == LogicalOperator.NOT and
            self._expressions_equal(clause1.operands[0], clause2)):
            return None  # Contradicción, cláusula vacía

        if (clause2.operator == LogicalOperator.NOT and
            self._expressions_equal(clause2.operands[0], clause1)):
            return None  # Contradicción, cláusula vacía

        # Si no hay complementarios, no se puede resolver
        return None

    def _is_tautology(self, clause: LogicalExpression) -> bool:
        """Verifica si una cláusula es una tautología"""
        if clause.operator == LogicalOperator.OR:
            # Verificar si contiene P y NOT(P)
            for i, op1 in enumerate(clause.operands):
                for op2 in clause.operands[i+1:]:
                    if (op1.operator == LogicalOperator.NOT and
                        self._expressions_equal(op1.operands[0], op2)):
                        return True
                    if (op2.operator == LogicalOperator.NOT and
                        self._expressions_equal(op2.operands[0], op1)):
                        return True
        return False

    def _clause_exists(self, clause: LogicalExpression, clauses: List[LogicalExpression]) -> bool:
        """Verifica si una cláusula ya existe"""
        return any(self._expressions_equal(clause, c) for c in clauses)

    def get_knowledge_base_state(self) -> Dict[str, Any]:
        """Obtiene el estado de la base de conocimiento"""
        return {
            'symbols': {name: {'type': sym.symbol_type.value, 'arity': sym.arity}
                      for name, sym in self.symbols.items()},
            'facts_count': len(self.facts),
            'rules_count': len(self.rules),
            'facts': [str(fact.expression) for fact in self.facts],
            'rules': [{'name': rule.name, 'confidence': rule.confidence}
                     for rule in self.rules]
        }


class ExpertSystem:
    """Sistema experto basado en reglas"""

    def __init__(self, domain: str):
        self.domain = domain
        self.reasoner = SymbolicReasoner()
        self.variables: Dict[str, Any] = {}

    def add_domain_knowledge(self, facts: List[str], rules: List[Dict[str, Any]]) -> None:
        """Agrega conocimiento del dominio"""
        # Agregar hechos
        for fact_str in facts:
            expression = self.reasoner.parse_expression(fact_str)
            self.reasoner.add_fact(expression)

        # Agregar reglas
        for rule_data in rules:
            premises = [self.reasoner.parse_expression(p) for p in rule_data['premises']]
            conclusion = self.reasoner.parse_expression(rule_data['conclusion'])
            self.reasoner.add_rule(
                name=rule_data['name'],
                premises=premises,
                conclusion=conclusion,
                confidence=rule_data.get('confidence', 1.0)
            )

    def diagnose(self, symptoms: List[str]) -> Dict[str, Any]:
        """Diagnóstico basado en síntomas"""
        # Agregar síntomas como hechos temporales
        symptom_facts = []
        for symptom in symptoms:
            try:
                expression = self.reasoner.parse_expression(symptom)
                self.reasoner.add_fact(expression, source="symptom")
                symptom_facts.append(str(expression))
            except:
                continue

        # Ejecutar encadenamiento hacia adelante
        goal = self.reasoner.parse_expression("diagnosis")
        success, trace = self.reasoner.forward_chaining(goal)

        # Limpiar hechos temporales
        self.reasoner.facts = [f for f in self.reasoner.facts if f.source != "symptom"]

        return {
            'success': success,
            'diagnosis': trace[-1]['conclusion'] if trace else "unknown",
            'trace': trace,
            'symptoms': symptom_facts
        }

    def explain(self, conclusion: str) -> List[Dict[str, Any]]:
        """Explica cómo se llegó a una conclusión"""
        expression = self.reasoner.parse_expression(conclusion)
        success, trace = self.reasoner.backward_chaining(expression)

        return trace


class LogicSolver:
    """Solucionador de problemas lógicos"""

    def __init__(self):
        self.reasoner = SymbolicReasoner()

    def solve_propositional_logic(self, premises: List[str], conclusion: str) -> Dict[str, Any]:
        """Resuelve un problema de lógica proposicional"""
        # Parsear premisas
        premise_expressions = [self.reasoner.parse_expression(p) for p in premises]
        conclusion_expr = self.reasoner.parse_expression(conclusion)

        # Agregar premisas como hechos
        for expr in premise_expressions:
            self.reasoner.add_fact(expr)

        # Verificar si la conclusión se sigue
        success, trace = self.reasoner.forward_chaining(conclusion_expr)

        return {
            'valid': success,
            'trace': trace,
            'premises': premises,
            'conclusion': conclusion
        }

    def check_validity(self, expression: str) -> bool:
        """Verifica la validez de una expresión lógica"""
        expr = self.reasoner.parse_expression(expression)

        # Una expresión es válida si es verdadera para todas las asignaciones
        # Para simplificar, verificamos algunas asignaciones comunes
        test_assignments = [
            {},
            {'P': True},
            {'P': False},
            {'P': True, 'Q': True},
            {'P': True, 'Q': False},
            {'P': False, 'Q': True},
            {'P': False, 'Q': False},
        ]

        for assignment in test_assignments:
            try:
                if not self.reasoner.evaluate_expression(expr, assignment):
                    return False
            except:
                continue

        return True


# Instancias globales
symbolic_reasoner = SymbolicReasoner()
expert_system = ExpertSystem("general")
logic_solver = LogicSolver()
