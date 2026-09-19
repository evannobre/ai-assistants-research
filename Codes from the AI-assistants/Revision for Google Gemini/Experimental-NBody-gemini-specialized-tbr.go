package main

import (
	"flag"
	"fmt"
	"math"
)

const (
	pi        = 3.141592653589793
	days      = 365.24
	solarMass = 4 * pi * pi
)

// Body represents a planetary body with 3D coordinates, velocity, and mass.
type Body struct {
	x, y, z    float64
	vx, vy, vz float64
	mass       float64
}

// advance updates the velocities and positions of all bodies by time step dt.
// This is the core algorithmic bottleneck, optimized by minimizing allocations
// and computing distance squared before the expensive square root.
func advance(bodies []Body, dt float64) {
	for i := 0; i < len(bodies); i++ {
		for j := i + 1; j < len(bodies); j++ {
			dx := bodies[i].x - bodies[j].x
			dy := bodies[i].y - bodies[j].y
			dz := bodies[i].z - bodies[j].z

			distSq := dx*dx + dy*dy + dz*dz
			dist := math.Sqrt(distSq)
			mag := dt / (distSq * dist)

			bodies[i].vx -= dx * bodies[j].mass * mag
			bodies[i].vy -= dy * bodies[j].mass * mag
			bodies[i].vz -= dz * bodies[j].mass * mag

			bodies[j].vx += dx * bodies[i].mass * mag
			bodies[j].vy += dy * bodies[i].mass * mag
			bodies[j].vz += dz * bodies[i].mass * mag
		}
	}

	for i := 0; i < len(bodies); i++ {
		bodies[i].x += dt * bodies[i].vx
		bodies[i].y += dt * bodies[i].vy
		bodies[i].z += dt * bodies[i].vz
	}
}

// energy calculates the total kinetic and potential energy of the system.
// Used to verify that the simulation conserves energy over time.
func energy(bodies []Body) float64 {
	e := 0.0
	for i := 0; i < len(bodies); i++ {
		e += 0.5 * bodies[i].mass * (bodies[i].vx*bodies[i].vx + bodies[i].vy*bodies[i].vy + bodies[i].vz*bodies[i].vz)
		for j := i + 1; j < len(bodies); j++ {
			dx := bodies[i].x - bodies[j].x
			dy := bodies[i].y - bodies[j].y
			dz := bodies[i].z - bodies[j].z
			dist := math.Sqrt(dx*dx + dy*dy + dz*dz)
			e -= (bodies[i].mass * bodies[j].mass) / dist
		}
	}
	return e
}

func main() {
	// Expose a command-line flag for benchmarking
	n := flag.Int("n", 1000, "number of iterations to simulate")
	flag.Parse()

	// Initial coordinates and velocities for the Jovian system
	bodies := []Body{
		// Sun
		{0, 0, 0, 0, 0, 0, solarMass},
		// Jupiter
		{4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01,
			1.66007664274403694e-03 * days, 7.69901118419740425e-03 * days, -6.90460016972063023e-05 * days,
			9.54791938424326609e-04 * solarMass},
		// Saturn
		{8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01,
			-2.76742510726862411e-03 * days, 4.99852801234917238e-03 * days, 2.30417297573763929e-05 * days,
			2.85885980666130812e-04 * solarMass},
		// Uranus
		{1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01,
			2.96460137564761618e-03 * days, 2.37847173959480950e-03 * days, -2.96589568540237556e-05 * days,
			4.36624404335156298e-05 * solarMass},
		// Neptune
		{1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01,
			2.68067772490389322e-03 * days, 1.62824170038242295e-03 * days, -9.51592254519715870e-05 * days,
			5.15138902046611451e-05 * solarMass},
	}

	// Offset the initial momentum of the Sun so that the center of mass remains at the origin
	px, py, pz := 0.0, 0.0, 0.0
	for _, b := range bodies {
		px += b.vx * b.mass
		py += b.vy * b.mass
		pz += b.vz * b.mass
	}
	bodies[0].vx = -px / solarMass
	bodies[0].vy = -py / solarMass
	bodies[0].vz = -pz / solarMass

	// Print initial energy
	fmt.Printf("%.9f\n", energy(bodies))

	// Run the simulation loop
	for i := 0; i < *n; i++ {
		advance(bodies, 0.01)
	}

	// Print final energy to verify simulation integrity
	fmt.Printf("%.9f\n", energy(bodies))
}