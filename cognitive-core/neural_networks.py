"""
Módulo de Neuronas Artificiales (Conexionismo/Deep Learning)
Implementa redes neuronales para reconocimiento de patrones y aprendizaje.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class ActivationFunction(Enum):
    """Funciones de activación para neuronas"""
    SIGMOID = "sigmoid"
    RELU = "relu"
    TANH = "tanh"
    SOFTMAX = "softmax"


class LayerType(Enum):
    """Tipos de capas neuronales"""
    DENSE = "dense"
    CONVOLUTIONAL = "convolutional"
    RECURRENT = "recurrent"
    ATTENTION = "attention"


@dataclass
class NeuralLayer:
    """Representa una capa de red neuronal"""
    layer_type: LayerType
    units: int
    activation: ActivationFunction
    input_shape: Optional[Tuple[int, ...]] = None
    weights: Optional[np.ndarray] = None
    biases: Optional[np.ndarray] = None


@dataclass
class NeuralNetworkConfig:
    """Configuración de una red neuronal"""
    layers: List[NeuralLayer]
    learning_rate: float = 0.01
    epochs: int = 100
    batch_size: int = 32
    optimizer: str = "adam"
    loss_function: str = "mse"


class NeuralNetwork:
    """Red neuronal artificial simplificada para reconocimiento de patrones"""

    def __init__(self, config: NeuralNetworkConfig):
        self.config = config
        self.layers = config.layers
        self.learning_rate = config.learning_rate
        self.is_trained = False
        self._initialize_weights()

    def _initialize_weights(self) -> None:
        """Inicializa pesos y sesgos de las capas"""
        for i, layer in enumerate(self.layers):
            if layer.layer_type == LayerType.DENSE:
                if i == 0:
                    # Capa de entrada
                    input_size = layer.input_shape[0] if layer.input_shape else 10
                else:
                    input_size = self.layers[i-1].units

                # Inicialización Xavier/Glorot
                layer.weights = np.random.randn(input_size, layer.units) * np.sqrt(2.0 / (input_size + layer.units))
                layer.biases = np.zeros((1, layer.units))

    def forward(self, inputs: np.ndarray) -> np.ndarray:
        """Propagación hacia adelante"""
        activation = inputs
        self.activations = [activation]

        for layer in self.layers:
            if layer.layer_type == LayerType.DENSE:
                z = np.dot(activation, layer.weights) + layer.biases
                activation = self._apply_activation(z, layer.activation)
                self.activations.append(activation)

        return activation

    def _apply_activation(self, z: np.ndarray, activation: ActivationFunction) -> np.ndarray:
        """Aplica función de activación"""
        if activation == ActivationFunction.SIGMOID:
            return 1.0 / (1.0 + np.exp(-z))
        elif activation == ActivationFunction.RELU:
            return np.maximum(0, z)
        elif activation == ActivationFunction.TANH:
            return np.tanh(z)
        elif activation == ActivationFunction.SOFTMAX:
            exp_z = np.exp(z - np.max(z, axis=1, keepdims=True))
            return exp_z / np.sum(exp_z, axis=1, keepdims=True)
        else:
            return z

    def backward(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Propagación hacia atrás (backpropagation)"""
        m = X.shape[0]
        output = self.forward(X)
        y_one_hot = self._one_hot_encode(y, output.shape[1])

        # Calcular error
        error = output - y_one_hot
        loss = np.mean(np.square(error))

        # Calcular gradientes
        gradients = []
        for i in reversed(range(len(self.layers))):
            layer = self.layers[i]
            if i == len(self.layers) - 1:
                # Capa de salida
                delta = error * self._activation_derivative(self.activations[i+1], layer.activation)
            else:
                # Capas ocultas
                delta = np.dot(delta, self.layers[i+1].weights.T) * \
                        self._activation_derivative(self.activations[i+1], layer.activation)

            if i > 0:
                dW = np.dot(self.activations[i].T, delta) / m
            else:
                dW = np.dot(X.T, delta) / m

            db = np.sum(delta, axis=0, keepdims=True) / m
            gradients.append({'dW': dW, 'db': db, 'layer_idx': i})

        # Actualizar pesos
        for grad in reversed(gradients):
            layer_idx = grad['layer_idx']
            self.layers[layer_idx].weights -= self.learning_rate * grad['dW']
            self.layers[layer_idx].biases -= self.learning_rate * grad['db']

        return {'loss': loss, 'accuracy': self._calculate_accuracy(output, y)}

    def _one_hot_encode(self, y: np.ndarray, num_classes: int) -> np.ndarray:
        """Codificación one-hot"""
        one_hot = np.zeros((y.shape[0], num_classes))
        one_hot[np.arange(y.shape[0]), y.astype(int)] = 1
        return one_hot

    def _activation_derivative(self, activation: np.ndarray, func: ActivationFunction) -> np.ndarray:
        """Derivada de la función de activación"""
        if func == ActivationFunction.SIGMOID:
            return activation * (1 - activation)
        elif func == ActivationFunction.RELU:
            return (activation > 0).astype(float)
        elif func == ActivationFunction.TANH:
            return 1 - np.square(activation)
        else:
            return np.ones_like(activation)

    def _calculate_accuracy(self, predictions: np.ndarray, y: np.ndarray) -> float:
        """Calcula precisión"""
        predicted_classes = np.argmax(predictions, axis=1)
        return np.mean(predicted_classes == y)

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = None) -> List[Dict[str, float]]:
        """Entrena la red neuronal"""
        if epochs is None:
            epochs = self.config.epochs

        history = []
        for epoch in range(epochs):
            metrics = self.backward(X, y)
            history.append(metrics)

            if epoch % 10 == 0:
                print(f"Epoch {epoch}: Loss = {metrics['loss']:.4f}, Accuracy = {metrics['accuracy']:.4f}")

        self.is_trained = True
        return history

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Realiza predicciones"""
        if not self.is_trained:
            raise RuntimeError("Network must be trained before prediction")
        output = self.forward(X)
        return np.argmax(output, axis=1)

    def get_weights(self) -> List[Dict[str, Any]]:
        """Obtiene los pesos de la red"""
        weights_info = []
        for i, layer in enumerate(self.layers):
            if layer.weights is not None:
                weights_info.append({
                    'layer': i,
                    'type': layer.layer_type.value,
                    'shape': layer.weights.shape,
                    'mean': np.mean(layer.weights),
                    'std': np.std(layer.weights)
                })
        return weights_info


class PatternRecognizer:
    """Reconocedor de patrones usando redes neuronales"""

    def __init__(self):
        self.network = None
        self.patterns = {}

    def create_network(self, input_size: int, hidden_layers: List[int], output_size: int) -> None:
        """Crea una red neuronal para reconocimiento de patrones"""
        layers = []

        # Capa de entrada
        layers.append(NeuralLayer(
            layer_type=LayerType.DENSE,
            units=hidden_layers[0],
            activation=ActivationFunction.RELU,
            input_shape=(input_size,)
        ))

        # Capas ocultas
        for i in range(1, len(hidden_layers)):
            layers.append(NeuralLayer(
                layer_type=LayerType.DENSE,
                units=hidden_layers[i],
                activation=ActivationFunction.RELU
            ))

        # Capa de salida
        layers.append(NeuralLayer(
            layer_type=LayerType.DENSE,
            units=output_size,
            activation=ActivationFunction.SOFTMAX
        ))

        config = NeuralNetworkConfig(layers=layers)
        self.network = NeuralNetwork(config)

    def train_pattern(self, pattern_name: str, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Entrena la red para reconocer un patrón específico"""
        if self.network is None:
            raise RuntimeError("Network not created. Call create_network first.")

        history = self.network.train(X, y, epochs=50)
        final_metrics = history[-1]

        self.patterns[pattern_name] = {
            'accuracy': final_metrics['accuracy'],
            'loss': final_metrics['loss'],
            'trained': True
        }

        return final_metrics

    def recognize_pattern(self, X: np.ndarray) -> Dict[str, Any]:
        """Reconoce patrones en los datos de entrada"""
        if self.network is None or not self.network.is_trained:
            raise RuntimeError("Network not trained")

        predictions = self.network.predict(X)
        confidence = self.network.forward(X)

        return {
            'predictions': predictions.tolist(),
            'confidence': confidence.tolist(),
            'pattern_name': self._get_pattern_name(predictions)
        }

    def _get_pattern_name(self, predictions: np.ndarray) -> str:
        """Obtiene el nombre del patrón basado en predicciones"""
        # Lógica simple para mapear predicciones a nombres de patrones
        pattern_names = list(self.patterns.keys())
        if pattern_names:
            return pattern_names[predictions[0] % len(pattern_names)]
        return "unknown"


class DeepLearningEngine:
    """Motor de Deep Learning para el cognitive core"""

    def __init__(self):
        self.pattern_recognizer = PatternRecognizer()
        self.active_networks = {}

    def create_pattern_network(self, network_id: str, input_size: int,
                               hidden_layers: List[int], output_size: int) -> None:
        """Crea una red neuronal para reconocimiento de patrones"""
        self.pattern_recognizer.create_network(input_size, hidden_layers, output_size)
        self.active_networks[network_id] = {
            'input_size': input_size,
            'hidden_layers': hidden_layers,
            'output_size': output_size,
            'created_at': np.datetime64('now').astype('datetime64[s]').astype(str)
        }

    def train_network(self, network_id: str, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Entrena una red neuronal específica"""
        if network_id not in self.active_networks:
            raise ValueError(f"Network {network_id} not found")

        metrics = self.pattern_recognizer.train_pattern(network_id, X, y)
        return metrics

    def recognize_patterns(self, network_id: str, X: np.ndarray) -> Dict[str, Any]:
        """Reconoce patrones usando una red específica"""
        if network_id not in self.active_networks:
            raise ValueError(f"Network {network_id} not found")

        return self.pattern_recognizer.recognize_pattern(X)

    def get_network_info(self, network_id: str) -> Dict[str, Any]:
        """Obtiene información de una red neuronal"""
        if network_id not in self.active_networks:
            raise ValueError(f"Network {network_id} not found")

        network_info = self.active_networks[network_id].copy()
        if self.pattern_recognizer.network:
            network_info['weights'] = self.pattern_recognizer.network.get_weights()
            network_info['is_trained'] = self.pattern_recognizer.network.is_trained

        return network_info

    def list_networks(self) -> Dict[str, Dict[str, Any]]:
        """Lista todas las redes neuronales activas"""
        return self.active_networks.copy()


# Instancia global del motor de Deep Learning
deep_learning_engine = DeepLearningEngine()
