import numpy as np
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from mesh.vertex import Vertex
    from mesh.edge import Edge

class Face:
    def __init__(self, index: int, vertices: List["Vertex"]):
        self.index = index
        self.vertices = vertices
        self.normal = self.compute_normal()
        self.centre = self.compute_centre()
        self.edges: List["Edge"] = []
        self.mask: bool = True # Used for marking faces during simplification
    
    def compute_normal(self):
        v1 = self.vertices[0].position
        v2 = self.vertices[1].position
        v3 = self.vertices[2].position
        normal = np.cross(v2 - v1, v3 - v1)
        normal /= np.linalg.norm(normal)

        return normal
    
    def add_edge(self, edge: "Edge"):
        self.edges.append(edge)
    
    def compute_centre(self):
        return np.mean([v.position for v in self.vertices], axis=0)
    
    def __eq__(self, other):
        if not isinstance(other, Face):
            return False
        return self.index == other.index
    
    def __hash__(self):
        return hash((self.index, tuple(v.index for v in self.vertices)))
    
    def __repr__(self):
        return f"Face(index={self.index}, vertices={[v.index for v in self.vertices]}, edges={[(e.vertices[0].index, e.vertices[1].index) for e in self.edges]})"