import sys, math, time

SOLAR_MASS = 4.0 * math.pi * math.pi
DAYS_PER_YEAR = 365.24

# initialize bodies using the ephemeris (convert velocities by DAYS_PER_YEAR)
bodies = [
  {'r':(0.0,0.0,0.0),'v':(0.0,0.0,0.0),'m':SOLAR_MASS},
  {'r':(4.8414314424647209,-1.1603200440274284,-0.10362204447112311),
   'v':(1.66007664274403694e-03*DAYS_PER_YEAR,7.69901118419740425e-03*DAYS_PER_YEAR,-6.90460016972063023e-05*DAYS_PER_YEAR),
   'm':9.54791938424326609e-04*SOLAR_MASS},
  # ... Saturn, Uranus, Neptune entries ...
]

def step(bodies, dt):
  N = len(bodies)
  acc = [ (0.0,0.0,0.0) for _ in range(N) ]
  for i in range(N):
    xi,yi,zi = bodies[i]['r']
    for j in range(N):
      if i==j: continue
      xj,yj,zj = bodies[j]['r']
      dx,dy,dz = xj-xi, yj-yi, zj-zi
      dist2 = dx*dx + dy*dy + dz*dz
      inv = 1.0 / math.sqrt(dist2)
      inv3 = inv*inv*inv
      mj = bodies[j]['m']
      ax = mj * dx * inv3
      ay = mj * dy * inv3
      az = mj * dz * inv3
      acc[i] = (acc[i][0]+ax, acc[i][1]+ay, acc[i][2]+az)
  for i in range(N):
    vx,vy,vz = bodies[i]['v']
    ax,ay,az = acc[i]
    vx += dt*ax; vy += dt*ay; vz += dt*az
    bodies[i]['v'] = (vx,vy,vz)
  for i in range(N):
    x,y,z = bodies[i]['r']
    vx,vy,vz = bodies[i]['v']
    bodies[i]['r'] = (x+dt*vx, y+dt*vy, z+dt*vz)

if __name__ == '__main__':
  n = int(sys.argv[1]) if len(sys.argv)>1 else 1000
  dt = 0.01
  t0 = time.time()
  for _ in range(n):
    step(bodies, dt)
  print('done', time.time()-t0)
