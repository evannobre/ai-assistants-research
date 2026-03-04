Body:
  x, y, z   : float64
  vx, vy, vz: float64
  mass      : float64

function offset_momentum(bodies):
  px = py = pz = 0
  for b in bodies:
    px += b.vx * b.mass
    py += b.vy * b.mass
    pz += b.vz * b.mass

  sun = bodies[0]           // assume index 0 is Sun
  sun.vx = -px / sun.mass
  sun.vy = -py / sun.mass
  sun.vz = -pz / sun.mass

function advance(bodies, dt):
  // Kick: pairwise velocity updates (Newton's third law keeps momentum consistent)
  for i in 0..len(bodies)-1:
    for j in i+1..len(bodies)-1:
      dx = bodies[i].x - bodies[j].x
      dy = bodies[i].y - bodies[j].y
      dz = bodies[i].z - bodies[j].z

      d2 = dx*dx + dy*dy + dz*dz
      dist = sqrt(d2)
      mag = dt / (d2 * dist)      // == dt / |r|^3

      mi = bodies[i].mass
      mj = bodies[j].mass

      // i feels j
      bodies[i].vx -= dx * mj * mag
      bodies[i].vy -= dy * mj * mag
      bodies[i].vz -= dz * mj * mag

      // j feels i (equal and opposite)
      bodies[j].vx += dx * mi * mag
      bodies[j].vy += dy * mi * mag
      bodies[j].vz += dz * mi * mag

  // Drift: position updates using new velocities
  for b in bodies:
    b.x += dt * b.vx
    b.y += dt * b.vy
    b.z += dt * b.vz

function energy(bodies):
  e = 0

  // kinetic
  for b in bodies:
    e += 0.5 * b.mass * (b.vx*b.vx + b.vy*b.vy + b.vz*b.vz)

  // potential
  for i in 0..len(bodies)-1:
    for j in i+1..len(bodies)-1:
      dx = bodies[i].x - bodies[j].x
      dy = bodies[i].y - bodies[j].y
      dz = bodies[i].z - bodies[j].z
      dist = sqrt(dx*dx + dy*dy + dz*dz)
      e -= (bodies[i].mass * bodies[j].mass) / dist

  return e

function main(argv):
  N = parse_int(argv[1], default=100000)   // performance knob
  dt = 0.01

  bodies = init_sun_and_jovians()          // constants embedded in source

  offset_momentum(bodies)

  print(energy(bodies))                    // optional correctness check

  repeat k in 1..N:
    advance(bodies, dt)

  print(energy(bodies))                    // optional correctness check
