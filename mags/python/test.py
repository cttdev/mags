import casadi as ca
import numpy as np

import matplotlib.pyplot as plt

opti = ca.Opti()
N = 200

start = [1.1, 1.1]
end = [8.2, 9.5]

# Sate variables
X = opti.variable(4, N+1)
xp = X[0, :]
yp = X[1, :]
xdot = X[2, :]
ydot = X[3, :]

# Control variables
U = opti.variable(2, N)
xdotdot = U[0, :]
ydotdot = U[1, :]

dt = opti.variable()

T = dt * N
opti.minimize(T)

# Dynamic model
def f(x, u):
    return ca.vertcat(
        x[2],
        x[3],
        u[0],
        u[1]
    )


for i in range(N):
    x_next = X[:, i] + dt * f(X[:, i], U[:, i])
    opti.subject_to(X[:, i+1] == x_next)

ox = np.linspace(1, 9, 8)
oy = np.linspace(1, 9, 8)

for i in range(N):
    # State constraints
    opti.subject_to(opti.bounded(-10, xdot[i], 10))
    opti.subject_to(opti.bounded(-10, ydot[i], 10))

    # Control constraints
    opti.subject_to(opti.bounded(-10, xdotdot[i], 10))
    opti.subject_to(opti.bounded(-10, ydotdot[i], 10))

    # Obstacle Constraints
    for j in range(len(ox)):
        for k in range(len(oy)):
            opti.subject_to((xp[i] - ox[j])**2 + (yp[i] - oy[k])**2 >= 0.1**2)

# Initial conditions
opti.subject_to(xp[0] == start[0])
opti.subject_to(yp[0] == start[1])

opti.subject_to(xdot[0] == 0)
opti.subject_to(ydot[0] == 0)

opti.subject_to(xdotdot[0] == 0)
opti.subject_to(ydotdot[0] == 0)

# Final conditions
opti.subject_to(xp[-1] == end[0])
opti.subject_to(yp[-1] == end[1])

opti.subject_to(xdot[-1] == 0)
opti.subject_to(ydot[-1] == 0)

opti.subject_to(xdotdot[-1] == 0)
opti.subject_to(ydotdot[-1] == 0)

opti.set_initial(dt, 0.1)

# Straight line initila guess
opti.set_initial(xp, ca.linspace(start[0], end[0], N+1))
opti.set_initial(yp, ca.linspace(start[1], end[1], N+1))

opti.set_initial(xdot, np.ones(N+1))
opti.set_initial(ydot, np.ones(N+1))

opti.set_initial(xdotdot, np.ones(N))
opti.set_initial(ydotdot, np.ones(N))

# def opti_callback(i):
#     plt.clf()
#     plt.plot(opti.debug.value(xp), opti.debug.value(yp))
#     plt.pause(0.1)

# opti.callback(opti_callback)
opti.solver("ipopt")
sol = opti.solve()


for i in range(len(ox)):
    for j in range(len(oy)):
        # PLot obstacles as circles
        circle = plt.Circle((ox[i], oy[j]), 0.1, color='r')

        # Add cirictcle patch to axis
        plt.gca().add_patch(circle)

plt.plot(sol.value(xp), sol.value(yp))
# Square acis
plt.axis('square')
plt.show()