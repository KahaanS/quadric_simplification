import numpy as np
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from mesh.vertex import Vertex
    from mesh.face import Face

class Edge:
    def __init__(self, vertex1: "Vertex", vertex2: "Vertex"):
        self.vertices = (vertex1, vertex2)
        self.faces: List["Face"] = []
        self.optimal_point = None  # Optimal position after collapse
        self.error = None  # Will be computed later
        self.mask = True  # Used for marking edges during simplification

    def add_face(self, face: "Face"):
        self.faces.append(face)

    def compute_error(self):
        v1, v2 = self.vertices
        Q = v1.quadric + v2.quadric

        # Construct Q' by replacing the last row to enforce the homogeneous constraint
        Q_prime = Q.copy()
        Q_prime[3, :] = np.array([0, 0, 0, 1])

        try:
            v_opt = np.linalg.solve(Q_prime, np.array([0, 0, 0, 1]))
            self.optimal_point = v_opt[:3]
            self.error = v_opt.T @ Q @ v_opt
        except np.linalg.LinAlgError:
            # If Q' is singular, use midpoint
            midpoint = (v1.position + v2.position) / 2.0
            v_hom = np.append(midpoint, 1.0)
            self.optimal_point = midpoint
            self.error = v_hom.T @ Q @ v_hom

    def __eq__(self, other):
        return set(self.vertices) == set(other.vertices)

    def __hash__(self):
        return hash(frozenset(self.vertices))

    def __repr__(self):
        return f"Edge(vertex1={self.vertices[0].index}, vertex2={self.vertices[1].index}, faces={[f.index for f in self.faces]}, error={self.error})"
