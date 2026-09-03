"""
Memoria Asociativa Vectorial
Implementa redes de Hopfield y memoria asociativa para recuperación de patrones.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class MemoryType(Enum):
    """Tipos de memoria asociativa"""
    HOPFIELD = "hopfield"
    BIDIRECTIONAL = "bidirectional"
    AUTOENCODER = "autoencoder"
    CONTENT_ADDRESSABLE = "content_addressable"


@dataclass
class MemoryPattern:
    """Patrón de memoria"""
    id: str
    vector: np.ndarray
    label: str
    metadata: Dict[str, Any]
    timestamp: str


class HopfieldNetwork:
    """Red de Hopfield para memoria asociativa"""

    def __init__(self, size: int):
        self.size = size
        self.weights = np.zeros((size, size))
        self.patterns: List[MemoryPattern] = []
        self.is_trained = False

    def train(self, patterns: List[np.ndarray]) -> None:
        """Entrena la red con patrones usando regla de Hebb"""
        self.patterns = patterns
        self.weights = np.zeros((self.size, self.size))

        for pattern in patterns:
            # Convertir a bipolar (-1, 1)
            pattern_bipolar = np.where(pattern > 0.5, 1, -1)

            # Regla de Hebb: W = (1/N) * sum(p_i * p_j^T)
            self.weights += np.outer(pattern_bipolar, pattern_bipolar)

        # Normalizar pesos
        self.weights /= len(patterns)

        # Eliminar conexiones propias
        np.fill_diagonal(self.weights, 0)

        self.is_trained = True

    def recall(self, pattern: np.ndarray, max_iterations: int = 100) -> np.ndarray:
        """Recupera un patrón desde una versión corrupta"""
        if not self.is_trained:
            raise RuntimeError("Network must be trained before recall")

        current_pattern = pattern.copy()
        pattern_bipolar = np.where(current_pattern > 0.5, 1, -1)

        for _ in range(max_iterations):
            # Actualizar cada neurona
            new_pattern = pattern_bipolar.copy()

            for i in range(self.size):
                activation = np.dot(self.weights[i], pattern_bipolar)
                new_pattern[i] = 1 if activation >= 0 else -1

            # Verificar convergencia
            if np.array_equal(new_pattern, pattern_bipolar):
                break

            pattern_bipolar = new_pattern

        # Convertir de vuelta a binario (0, 1)
        return np.where(pattern_bipolar > 0, 1, 0)

    def energy(self, pattern: np.ndarray) -> float:
        """Calcula la energía de un patrón"""
        pattern_bipolar = np.where(pattern > 0.5, 1, -1)
        return -0.5 * np.dot(pattern_bipolar, np.dot(self.weights, pattern_bipolar))

    def capacity(self) -> int:
        """Estima la capacidad de la red (0.138 * N)"""
        return int(0.138 * self.size)


class BidirectionalMemory:
    """Memoria Bidireccional (BAM)"""

    def __init__(self, input_size: int, output_size: int):
        self.input_size = input_size
        self.output_size = output_size
        self.weights = np.zeros((input_size, output_size))
        self.patterns: List[Tuple[np.ndarray, np.ndarray]] = []
        self.is_trained = False

    def train(self, pattern_pairs: List[Tuple[np.ndarray, np.ndarray]]) -> None:
        """Entrena la memoria con pares de patrones"""
        self.patterns = pattern_pairs
        self.weights = np.zeros((self.input_size, self.output_size))

        for input_pattern, output_pattern in pattern_pairs:
            # Convertir a bipolar
            input_bipolar = np.where(input_pattern > 0.5, 1, -1)
            output_bipolar = np.where(output_pattern > 0.5, 1, -1)

            # Regla de Hebb
            self.weights += np.outer(input_bipolar, output_bipolar)

        self.weights /= len(pattern_pairs)
        self.is_trained = True

    def recall_output(self, input_pattern: np.ndarray) -> np.ndarray:
        """Recupera el patrón de salida desde la entrada"""
        if not self.is_trained:
            raise RuntimeError("Memory must be trained before recall")

        input_bipolar = np.where(input_pattern > 0.5, 1, -1)
        output_activation = np.dot(input_bipolar, self.weights)
        output_pattern = np.where(output_activation >= 0, 1, 0)

        return output_pattern

    def recall_input(self, output_pattern: np.ndarray) -> np.ndarray:
        """Recupera el patrón de entrada desde la salida"""
        if not self.is_trained:
            raise RuntimeError("Memory must be trained before recall")

        output_bipolar = np.where(output_pattern > 0.5, 1, -1)
        input_activation = np.dot(output_bipolar, self.weights.T)
        input_pattern = np.where(input_activation >= 0, 1, 0)

        return input_pattern


class ContentAddressableMemory:
    """Memoria direccionable por contenido"""

    def __init__(self, vector_size: int, capacity: int = 1000):
        self.vector_size = vector_size
        self.capacity = capacity
        self.memory: List[MemoryPattern] = []
        self.index = {}  # Índice rápido por etiqueta

    def store(self, vector: np.ndarray, label: str, metadata: Dict[str, Any] = None) -> str:
        """Almacena un vector en memoria"""
        if len(self.memory) >= self.capacity:
            # Reemplazar el más antiguo (FIFO)
            removed = self.memory.pop(0)
            if removed.label in self.index:
                del self.index[removed.label]

        pattern_id = f"pattern_{len(self.memory)}"
        from datetime import datetime

        pattern = MemoryPattern(
            id=pattern_id,
            vector=vector,
            label=label,
            metadata=metadata or {},
            timestamp=datetime.now().isoformat()
        )

        self.memory.append(pattern)
        self.index[label] = pattern

        return pattern_id

    def retrieve(self, query_vector: np.ndarray, k: int = 5) -> List[MemoryPattern]:
        """Recupera los k vectores más similares"""
        if not self.memory:
            return []

        similarities = []
        for pattern in self.memory:
            similarity = self._cosine_similarity(query_vector, pattern.vector)
            similarities.append((similarity, pattern))

        # Ordenar por similitud descendente
        similarities.sort(key=lambda x: x[0], reverse=True)

        return [pattern for _, pattern in similarities[:k]]

    def retrieve_by_label(self, label: str) -> Optional[MemoryPattern]:
        """Recupera un patrón por su etiqueta"""
        return self.index.get(label)

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calcula similitud de coseno"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def forget(self, pattern_id: str) -> bool:
        """Olvida un patrón específico"""
        for i, pattern in enumerate(self.memory):
            if pattern.id == pattern_id:
                removed = self.memory.pop(i)
                if removed.label in self.index:
                    del self.index[removed.label]
                return True
        return False

    def get_memory_state(self) -> Dict[str, Any]:
        """Obtiene el estado de la memoria"""
        return {
            'capacity': self.capacity,
            'used': len(self.memory),
            'available': self.capacity - len(self.memory),
            'vector_size': self.vector_size,
            'labels': list(self.index.keys())
        }


class AssociativeMemoryEngine:
    """Motor de memoria asociativa que integra diferentes tipos"""

    def __init__(self):
        self.hopfield_networks: Dict[str, HopfieldNetwork] = {}
        self.bidirectional_memories: Dict[str, BidirectionalMemory] = {}
        self.content_addressable_memory = ContentAddressableMemory(vector_size=768)

    def create_hopfield_network(self, network_id: str, size: int) -> None:
        """Crea una red de Hopfield"""
        self.hopfield_networks[network_id] = HopfieldNetwork(size)

    def train_hopfield(self, network_id: str, patterns: List[np.ndarray]) -> None:
        """Entrena una red de Hopfield"""
        if network_id not in self.hopfield_networks:
            raise ValueError(f"Hopfield network {network_id} not found")

        self.hopfield_networks[network_id].train(patterns)

    def recall_hopfield(self, network_id: str, pattern: np.ndarray) -> np.ndarray:
        """Recupera un patrón usando Hopfield"""
        if network_id not in self.hopfield_networks:
            raise ValueError(f"Hopfield network {network_id} not found")

        return self.hopfield_networks[network_id].recall(pattern)

    def create_bidirectional_memory(self, memory_id: str, input_size: int, output_size: int) -> None:
        """Crea una memoria bidireccional"""
        self.bidirectional_memories[memory_id] = BidirectionalMemory(input_size, output_size)

    def train_bidirectional(self, memory_id: str, pattern_pairs: List[Tuple[np.ndarray, np.ndarray]]) -> None:
        """Entrena una memoria bidireccional"""
        if memory_id not in self.bidirectional_memories:
            raise ValueError(f"Bidirectional memory {memory_id} not found")

        self.bidirectional_memories[memory_id].train(pattern_pairs)

    def store_pattern(self, vector: np.ndarray, label: str, metadata: Dict[str, Any] = None) -> str:
        """Almacena un patrón en memoria direccionable por contenido"""
        return self.content_addressable_memory.store(vector, label, metadata)

    def retrieve_pattern(self, query_vector: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """Recupera patrones similares"""
        patterns = self.content_addressable_memory.retrieve(query_vector, k)
        return [
            {
                'id': p.id,
                'label': p.label,
                'metadata': p.metadata,
                'timestamp': p.timestamp
            }
            for p in patterns
        ]

    def associative_recall(self, partial_pattern: np.ndarray, memory_type: MemoryType = MemoryType.CONTENT_ADDRESSABLE) -> np.ndarray:
        """Recuerdo asociativo usando diferentes tipos de memoria"""
        if memory_type == MemoryType.CONTENT_ADDRESSABLE:
            patterns = self.content_addressable_memory.retrieve(partial_pattern, k=1)
            if patterns:
                return patterns[0].vector
            return partial_pattern

        elif memory_type == MemoryType.HOPFIELD:
            # Usar la primera red de Hopfield disponible
            if self.hopfield_networks:
                network_id = list(self.hopfield_networks.keys())[0]
                return self.hopfield_networks[network_id].recall(partial_pattern)
            return partial_pattern

        return partial_pattern

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de todas las memorias"""
        return {
            'hopfield_networks': {
                net_id: {
                    'size': net.size,
                    'patterns': len(net.patterns),
                    'capacity': net.capacity(),
                    'is_trained': net.is_trained
                }
                for net_id, net in self.hopfield_networks.items()
            },
            'bidirectional_memories': {
                mem_id: {
                    'input_size': mem.input_size,
                    'output_size': mem.output_size,
                    'patterns': len(mem.patterns),
                    'is_trained': mem.is_trained
                }
                for mem_id, mem in self.bidirectional_memories.items()
            },
            'content_addressable': self.content_addressable_memory.get_memory_state()
        }


# Instancia global del motor de memoria asociativa
associative_memory_engine = AssociativeMemoryEngine()
