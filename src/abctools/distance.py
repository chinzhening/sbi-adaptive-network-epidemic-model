import numpy as np

def euclidean(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.linalg.norm(a - b)
