import streamlit as st
import felupe as fem

st.title("A Streamlit app for FElupe")
n = st.slider("Number of points per axis", 2, 11, 3)
v = st.slider("Stretch", 1.0, 2.0, 2.0)

progress_bar = st.progress(0)
def show_progress(i, j, substep):
    progress_bar.progress((1 + j) / len(move))

mesh = fem.Cube(n=n).add_midpoints_edges().add_midpoints_faces().add_midpoints_volumes()
region = fem.RegionTriQuadraticHexahedron(mesh)
field = fem.FieldContainer([fem.Field(region, dim=3)])

boundaries, loadcase = fem.dof.uniaxial(field, clamped=True)
umat = fem.NeoHooke(mu=1, bulk=2)
solid = fem.SolidBody(umat=umat, field=field)
move = fem.math.linsteps([0, v - 1], num=5)

ramp = {boundaries["move"]: move}
step = fem.Step(items=[solid], ramp=ramp, boundaries=boundaries)
job = fem.Job(steps=[step], callback=show_progress)
job.evaluate(tol=1e-2)

img = solid.screenshot(show_undeformed=False, theme="static")
st.image("solidbody.png")

img = mesh.screenshot(show_edges=False, theme="static")
st.image("mesh.png")