"""
Módulo de Algoritmos Deterministas (Código Clásico)
Implementa algoritmos clásicos deterministas sin aleatoriedad ni aprendizaje.
"""

from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import heapq
import math
from abc import ABC, abstractmethod


class AlgorithmType(Enum):
    """Tipos de algoritmos deterministas"""
    SEARCH = "search"
    SORTING = "sorting"
    OPTIMIZATION = "optimization"
    PATHFINDING = "pathfinding"
    SCHEDULING = "scheduling"
    CLASSIFICATION = "classification"


@dataclass
class AlgorithmResult:
    """Resultado de un algoritmo determinista"""
    algorithm: str
    success: bool
    result: Any
    steps: int
    time_complexity: str
    space_complexity: str
    metadata: Dict[str, Any]


class DeterministicSearch:
    """Algoritmos de búsqueda deterministas"""

    @staticmethod
    def binary_search(arr: List, target: Any) -> AlgorithmResult:
        """Búsqueda binaria determinista"""
        steps = 0
        left, right = 0, len(arr) - 1

        while left <= right:
            steps += 1
            mid = (left + right) // 2

            if arr[mid] == target:
                return AlgorithmResult(
                    algorithm="binary_search",
                    success=True,
                    result=mid,
                    steps=steps,
                    time_complexity="O(log n)",
                    space_complexity="O(1)",
                    metadata={"found": True, "index": mid}
                )
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1

        return AlgorithmResult(
            algorithm="binary_search",
            success=False,
            result=None,
            steps=steps,
            time_complexity="O(log n)",
            space_complexity="O(1)",
            metadata={"found": False}
        )

    @staticmethod
    def linear_search(arr: List, target: Any) -> AlgorithmResult:
        """Búsqueda lineal determinista"""
        steps = 0

        for i, item in enumerate(arr):
            steps += 1
            if item == target:
                return AlgorithmResult(
                    algorithm="linear_search",
                    success=True,
                    result=i,
                    steps=steps,
                    time_complexity="O(n)",
                    space_complexity="O(1)",
                    metadata={"found": True, "index": i}
                )

        return AlgorithmResult(
            algorithm="linear_search",
            success=False,
            result=None,
            steps=steps,
            time_complexity="O(n)",
            space_complexity="O(1)",
            metadata={"found": False}
        )


class DeterministicSorting:
    """Algoritmos de ordenamiento deterministas"""

    @staticmethod
    def quick_sort(arr: List) -> AlgorithmResult:
        """QuickSort determinista (siempre usa el primer elemento como pivote)"""
        steps = 0
        arr_copy = arr.copy()

        def _quick_sort_helper(a: List, low: int, high: int) -> None:
            nonlocal steps
            if low < high:
                pivot_index = _partition(a, low, high)
                _quick_sort_helper(a, low, pivot_index - 1)
                _quick_sort_helper(a, pivot_index + 1, high)

        def _partition(a: List, low: int, high: int) -> int:
            nonlocal steps
            pivot = a[high]
            i = low - 1

            for j in range(low, high):
                steps += 1
                if a[j] <= pivot:
                    i += 1
                    a[i], a[j] = a[j], a[i]

            a[i + 1], a[high] = a[high], a[i + 1]
            return i + 1

        _quick_sort_helper(arr_copy, 0, len(arr_copy) - 1)

        return AlgorithmResult(
            algorithm="quick_sort",
            success=True,
            result=arr_copy,
            steps=steps,
            time_complexity="O(n log n)",
            space_complexity="O(log n)",
            metadata={"sorted": True}
        )

    @staticmethod
    def merge_sort(arr: List) -> AlgorithmResult:
        """MergeSort determinista"""
        steps = 0
        arr_copy = arr.copy()

        def _merge_sort_helper(a: List) -> List:
            nonlocal steps
            if len(a) <= 1:
                return a

            mid = len(a) // 2
            left = _merge_sort_helper(a[:mid])
            right = _merge_sort_helper(a[mid:])

            return _merge(left, right)

        def _merge(left: List, right: List) -> List:
            nonlocal steps
            result = []
            i = j = 0

            while i < len(left) and j < len(right):
                steps += 1
                if left[i] <= right[j]:
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1

            result.extend(left[i:])
            result.extend(right[j:])
            return result

        sorted_arr = _merge_sort_helper(arr_copy)

        return AlgorithmResult(
            algorithm="merge_sort",
            success=True,
            result=sorted_arr,
            steps=steps,
            time_complexity="O(n log n)",
            space_complexity="O(n)",
            metadata={"sorted": True}
        )


class DeterministicPathfinding:
    """Algoritmos de búsqueda de caminos deterministas"""

    @staticmethod
    def dijkstra(graph: Dict[str, Dict[str, int]], start: str, end: str) -> AlgorithmResult:
        """Algoritmo de Dijkstra determinista"""
        steps = 0
        distances = {node: float('inf') for node in graph}
        distances[start] = 0
        previous = {node: None for node in graph}
        visited = set()

        priority_queue = [(0, start)]

        while priority_queue:
            current_dist, current = heapq.heappop(priority_queue)

            if current in visited:
                continue

            visited.add(current)
            steps += 1

            if current == end:
                break

            for neighbor, weight in graph[current].items():
                if neighbor not in visited:
                    new_dist = current_dist + weight
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        previous[neighbor] = current
                        heapq.heappush(priority_queue, (new_dist, neighbor))

        # Reconstruir camino
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()

        return AlgorithmResult(
            algorithm="dijkstra",
            success=end in visited,
            result={
                "path": path,
                "distance": distances[end],
                "visited_nodes": list(visited)
            },
            steps=steps,
            time_complexity="O((V + E) log V)",
            space_complexity="O(V)",
            metadata={"graph_nodes": len(graph), "path_length": len(path)}
        )

    @staticmethod
    def a_star(graph: Dict[str, Dict[str, int]], start: str, end: str,
                heuristic: Callable[[str, str], float]) -> AlgorithmResult:
        """Algoritmo A* determinista"""
        steps = 0
        g_score = {node: float('inf') for node in graph}
        g_score[start] = 0
        f_score = {node: float('inf') for node in graph}
        f_score[start] = heuristic(start, end)
        previous = {node: None for node in graph}
        visited = set()

        priority_queue = [(f_score[start], start)]

        while priority_queue:
            current_f, current = heapq.heappop(priority_queue)

            if current in visited:
                continue

            visited.add(current)
            steps += 1

            if current == end:
                break

            for neighbor, weight in graph[current].items():
                if neighbor not in visited:
                    tentative_g = g_score[current] + weight
                    if tentative_g < g_score[neighbor]:
                        previous[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + heuristic(neighbor, end)
                        heapq.heappush(priority_queue, (f_score[neighbor], neighbor))

        # Reconstruir camino
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()

        return AlgorithmResult(
            algorithm="a_star",
            success=end in visited,
            result={
                "path": path,
                "distance": g_score[end],
                "visited_nodes": list(visited)
            },
            steps=steps,
            time_complexity="O((V + E) log V)",
            space_complexity="O(V)",
            metadata={"graph_nodes": len(graph), "path_length": len(path)}
        )


class DeterministicOptimization:
    """Algoritmos de optimización deterministas"""

    @staticmethod
    def dynamic_programming_knapsack(weights: List[int], values: List[int], capacity: int) -> AlgorithmResult:
        """Problema de la mochila con programación dinámica"""
        n = len(weights)
        dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
        steps = 0

        for i in range(1, n + 1):
            for w in range(capacity + 1):
                steps += 1
                if weights[i - 1] <= w:
                    dp[i][w] = max(
                        dp[i - 1][w],
                        dp[i - 1][w - weights[i - 1]] + values[i - 1]
                    )
                else:
                    dp[i][w] = dp[i - 1][w]

        # Reconstruir solución
        w = capacity
        selected_items = []
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                selected_items.append(i - 1)
                w -= weights[i - 1]

        return AlgorithmResult(
            algorithm="dynamic_programming_knapsack",
            success=True,
            result={
                "max_value": dp[n][capacity],
                "selected_items": selected_items,
                "total_weight": sum(weights[i] for i in selected_items)
            },
            steps=steps,
            time_complexity="O(nW)",
            space_complexity="O(nW)",
            metadata={"items": n, "capacity": capacity}
        )

    @staticmethod
    def greedy_activity_selection(start_times: List[int], end_times: List[int]) -> AlgorithmResult:
        """Selección de actividades greedy determinista"""
        activities = list(zip(start_times, end_times))
        activities.sort(key=lambda x: x[1])  # Ordenar por tiempo de finalización

        selected = []
        last_end = 0
        steps = 0

        for start, end in activities:
            steps += 1
            if start >= last_end:
                selected.append((start, end))
                last_end = end

        return AlgorithmResult(
            algorithm="greedy_activity_selection",
            success=True,
            result={
                "selected_activities": selected,
                "count": len(selected)
            },
            steps=steps,
            time_complexity="O(n log n)",
            space_complexity="O(n)",
            metadata={"total_activities": len(activities)}
        )


class DeterministicScheduling:
    """Algoritmos de planificación deterministas"""

    @staticmethod
    def round_robin(processes: List[Dict[str, int]], time_quantum: int) -> AlgorithmResult:
        """Planificación Round Robin determinista"""
        steps = 0
        queue = processes.copy()
        current_time = 0
        completion_times = {}

        while queue:
            process = queue.pop(0)
            pid = process['pid']
            burst_time = process['burst_time']

            if burst_time <= time_quantum:
                current_time += burst_time
                completion_times[pid] = current_time
                steps += 1
            else:
                current_time += time_quantum
                process['burst_time'] -= time_quantum
                queue.append(process)
                steps += 1

        # Calcular tiempos de espera
        waiting_times = {}
        for process in processes:
            pid = process['pid']
            waiting_times[pid] = completion_times[pid] - process['burst_time']

        avg_waiting = sum(waiting_times.values()) / len(waiting_times)

        return AlgorithmResult(
            algorithm="round_robin",
            success=True,
            result={
                "completion_times": completion_times,
                "waiting_times": waiting_times,
                "average_waiting_time": avg_waiting
            },
            steps=steps,
            time_complexity="O(n)",
            space_complexity="O(n)",
            metadata={"time_quantum": time_quantum, "processes": len(processes)}
        )

    @staticmethod
    def shortest_job_first(processes: List[Dict[str, int]]) -> AlgorithmResult:
        """Planificación SJF (Shortest Job First) determinista"""
        steps = 0
        processes_sorted = sorted(processes, key=lambda x: x['burst_time'])
        current_time = 0
        completion_times = {}

        for process in processes_sorted:
            pid = process['pid']
            burst_time = process['burst_time']
            current_time += burst_time
            completion_times[pid] = current_time
            steps += 1

        # Calcular tiempos de espera
        waiting_times = {}
        for process in processes:
            pid = process['pid']
            waiting_times[pid] = completion_times[pid] - process['burst_time']

        avg_waiting = sum(waiting_times.values()) / len(waiting_times)

        return AlgorithmResult(
            algorithm="shortest_job_first",
            success=True,
            result={
                "completion_times": completion_times,
                "waiting_times": waiting_times,
                "average_waiting_time": avg_waiting
            },
            steps=steps,
            time_complexity="O(n log n)",
            space_complexity="O(n)",
            metadata={"processes": len(processes)}
        )


class DeterministicClassification:
    """Algoritmos de clasificación deterministas"""

    @staticmethod
    def k_nearest_neighbors(training_data: List[Tuple[List[float], str]],
                           test_point: List[float], k: int = 3) -> AlgorithmResult:
        """K-Nearest Neighbors determinista"""
        steps = 0
        distances = []

        for features, label in training_data:
            distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(features, test_point)))
            distances.append((distance, label))
            steps += 1

        distances.sort(key=lambda x: x[0])
        k_nearest = distances[:k]

        # Votación mayoritaria
        label_counts = {}
        for _, label in k_nearest:
            label_counts[label] = label_counts.get(label, 0) + 1

        predicted_label = max(label_counts.items(), key=lambda x: x[1])[0]

        return AlgorithmResult(
            algorithm="k_nearest_neighbors",
            success=True,
            result={
                "predicted_label": predicted_label,
                "neighbors": [(d, l) for d, l in k_nearest],
                "label_counts": label_counts
            },
            steps=steps,
            time_complexity="O(n)",
            space_complexity="O(n)",
            metadata={"k": k, "training_samples": len(training_data)}
        )

    @staticmethod
    def decision_tree_simple(features: List[float], thresholds: List[float],
                           labels: List[str]) -> AlgorithmResult:
        """Árbol de decisión simple determinista"""
        steps = 0
        current_node = 0

        while current_node < len(thresholds):
            steps += 1
            if features[current_node] <= thresholds[current_node]:
                # Ir a la izquierda
                current_node = 2 * current_node + 1
            else:
                # Ir a la derecha
                current_node = 2 * current_node + 2

            if current_node >= len(thresholds):
                break

        # Si llegamos a una hoja, devolver la etiqueta correspondiente
        if current_node < len(labels):
            predicted_label = labels[current_node]
        else:
            predicted_label = labels[-1]

        return AlgorithmResult(
            algorithm="decision_tree_simple",
            success=True,
            result={
                "predicted_label": predicted_label,
                "final_node": current_node
            },
            steps=steps,
            time_complexity="O(d)",
            space_complexity="O(1)",
            metadata={"depth": len(thresholds)}
        )


class DeterministicAlgorithmEngine:
    """Motor de algoritmos deterministas"""

    def __init__(self):
        self.search = DeterministicSearch()
        self.sorting = DeterministicSorting()
        self.pathfinding = DeterministicPathfinding()
        self.optimization = DeterministicOptimization()
        self.scheduling = DeterministicScheduling()
        self.classification = DeterministicClassification()

    def execute_algorithm(self, algorithm_type: AlgorithmType, algorithm_name: str,
                          **kwargs) -> AlgorithmResult:
        """Ejecuta un algoritmo determinista específico"""
        if algorithm_type == AlgorithmType.SEARCH:
            if algorithm_name == "binary_search":
                return self.search.binary_search(kwargs['arr'], kwargs['target'])
            elif algorithm_name == "linear_search":
                return self.search.linear_search(kwargs['arr'], kwargs['target'])

        elif algorithm_type == AlgorithmType.SORTING:
            if algorithm_name == "quick_sort":
                return self.sorting.quick_sort(kwargs['arr'])
            elif algorithm_name == "merge_sort":
                return self.sorting.merge_sort(kwargs['arr'])

        elif algorithm_type == AlgorithmType.PATHFINDING:
            if algorithm_name == "dijkstra":
                return self.pathfinding.dijkstra(kwargs['graph'], kwargs['start'], kwargs['end'])
            elif algorithm_name == "a_star":
                return self.pathfinding.a_star(kwargs['graph'], kwargs['start'], kwargs['end'],
                                             kwargs['heuristic'])

        elif algorithm_type == AlgorithmType.OPTIMIZATION:
            if algorithm_name == "knapsack":
                return self.optimization.dynamic_programming_knapsack(
                    kwargs['weights'], kwargs['values'], kwargs['capacity']
                )
            elif algorithm_name == "activity_selection":
                return self.optimization.greedy_activity_selection(
                    kwargs['start_times'], kwargs['end_times']
                )

        elif algorithm_type == AlgorithmType.SCHEDULING:
            if algorithm_name == "round_robin":
                return self.scheduling.round_robin(kwargs['processes'], kwargs['time_quantum'])
            elif algorithm_name == "shortest_job_first":
                return self.scheduling.shortest_job_first(kwargs['processes'])

        elif algorithm_type == AlgorithmType.CLASSIFICATION:
            if algorithm_name == "knn":
                return self.classification.k_nearest_neighbors(
                    kwargs['training_data'], kwargs['test_point'], kwargs.get('k', 3)
                )
            elif algorithm_name == "decision_tree":
                return self.classification.decision_tree_simple(
                    kwargs['features'], kwargs['thresholds'], kwargs['labels']
                )

        raise ValueError(f"Unknown algorithm: {algorithm_name}")

    def get_available_algorithms(self) -> Dict[str, List[str]]:
        """Obtiene lista de algoritmos disponibles"""
        return {
            "search": ["binary_search", "linear_search"],
            "sorting": ["quick_sort", "merge_sort"],
            "pathfinding": ["dijkstra", "a_star"],
            "optimization": ["knapsack", "activity_selection"],
            "scheduling": ["round_robin", "shortest_job_first"],
            "classification": ["knn", "decision_tree"]
        }


# Instancia global del motor de algoritmos deterministas
deterministic_engine = DeterministicAlgorithmEngine()
