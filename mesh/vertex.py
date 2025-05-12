import numpy as np
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from mesh.face import Face
    from mesh.edge import Edge

class Vertex:
    def __init__(self, index, position):
        self.index = index
        self.position = np.array(position)
        self.edges: List["Edge"] = []
        self.faces: List["Face"] = []
        self.quadric = np.zeros((4, 4))  # Quadric error metric
        self.mask: bool = True  # Used for marking vertices during simplification

    def add_edge(self, edge: "Edge"):
        self.edges.append(edge)

    def add_face(self, face: "Face"):
        self.faces.append(face)
            
    def compute_quadric(self):
        quadric = np.zeros((4, 4))
        for face in self.faces:
            normal = face.normal
            d = -np.dot(normal, face.centre)
            plane = np.array([normal[0], normal[1], normal[2], d])
            quadric += np.outer(plane, plane)
        assert quadric.shape == (4, 4), "Quadric matrix should be 4x4"
        self.quadric = quadric
    
    def __eq__(self, other):
        if not isinstance(other, Vertex):
            return False
        return self.index == other.index and np.array_equal(self.position, other.position)
    
    def __hash__(self):
        return hash((self.index, tuple(self.position)))
            
    def __repr__(self):
        return f"Vertex(index={self.index}, position={self.position}, faces={[f.index for f in self.faces]}, edges={[(e.vertices[0].index, e.vertices[1].index) for e in self.edges]})"