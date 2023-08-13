motion of vehicle:

1) longitudinal dynamics (basic forward-backward motion):
   a) engine force: torque produced by the engine divided by the wheel
   ![1691821237664](image/equations/1691821237664.png)
   b). aerodynamic drag (Fdrag): Proportional to the square of the vehicle's speed
   ![1691821217231](image/equations/1691821217231.png)
   c ) rolling resistance (Frolling): constant force opposing motion
   ![1691821196873](image/equations/1691821196873.png).> the net force Fnet in longitudinal direction
   ![1691821299054](image/equations/1691821299054.png)
2) Lateral dynamics (side to side motion):
   a) Cornering Force: proportional to the tire slip angle

   ![1691821399444](image/equations/1691821399444.png)

   assuming here there is no other significant lateral forces, so Flateral = Fcornering, we shall add slip angles, cornering stiffness

   ![1691821452031](image/equations/1691821452031.png)
3) equations of motion

   ![1691821588575](image/equations/1691821588575.png) ![1691821601824](image/equations/1691821601824.png)
4) braking: implemented braking as a negative torque, which opposes the motion of vehicle e.x., F_brake
5) traction control: means prevent wheel spin during acceleration by detecting wheel spin and reducing engine torque or applying brake force to specific wheels.
6) Turning control.

   dx/dt = v * cos(θ + δ)
   dy/dt = v * sin(θ + δ)
   dθ/dt = v / L * sin(δ)

   ![1691877495906](image/equations/1691877495906.png)
7)
