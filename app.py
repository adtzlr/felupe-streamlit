import streamlit as st
import felupe as fem
import pypardiso

from stpyvista.trame_backend import stpyvista
from stpyvista.utils import start_xvfb

start_xvfb()

st.title("A Streamlit app for FElupe")
npoints = st.sidebar.slider("Number of points per axis", 2, 7, 5)
stretch = st.sidebar.slider("Stretch", 0.7, 1.5, 0.7)

options = ["Hexahedron", "Tetra", "Quadratic Tetra"]
selection = st.sidebar.selectbox("Cell type", options)
topoints = st.sidebar.checkbox("Project stress to points")

mesh = fem.Cube(n=npoints)

if selection == "Hexahedron":
    region = fem.RegionHexahedron(mesh)
elif selection == "Tetra":
    region = fem.RegionTetra(mesh.triangulate())
elif selection == "Quadratic Tetra":
    region = fem.RegionQuadraticTetra(
        mesh.triangulate().add_midpoints_edges(),
        quadrature=fem.TetrahedronQuadrature(order=5),
    )
else:
    raise TypeError("Cell type not implemented.")

field = fem.FieldContainer(fields=[fem.Field(region, dim=3)])

boundaries, loadcase = fem.dof.uniaxial(field, clamped=True, move=stretch - 1)
solid = fem.SolidBody(umat=fem.NeoHooke(mu=1, bulk=5), field=field)

step = fem.Step(items=[solid], boundaries=boundaries)
job = fem.Job(steps=[step]).evaluate(tol=1e-2, solver=pypardiso.spsolve)

if topoints:
    project = fem.project
else:
    project = None

plotter = solid.plot(
    "Principal Values of Cauchy Stress", nonlinear_subdivision=2, project=project
)
stpyvista(plotter)
