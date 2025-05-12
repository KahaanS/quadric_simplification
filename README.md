## Quadric Error based Mesh Simplification

An implementation of Surface Simplification Using Quadric Error Metrics (Garland and Heckbert) for my Computer Graphics and Computational Imaging (Spring '25) course.

To simplify a mesh use [simplify.py](simplify.py). A sample command is as follows: ```python simplify.py -i samples/vase100k.obj -o output -r 0.5```. The ``` -r ``` flag gives the ratio to reduce by and the mesh is outputed in the output folder. I have provided one sample .obj file. Note that it only runs on faces with models that are manifold and have only triangular faces.

It should run out of the box with numpy. The evalution function requires the trimesh library. The batch_simplify and batch_eval scripts run on entire directories of input.