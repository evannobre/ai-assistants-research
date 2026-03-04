// nbody.go
package main

import (
    "fmt"
    "math"
    "os"
    "strconv"
    "time"
)

const (
    DAYS_PER_YEAR = 365.24
    SOLAR_MASS    = 4.0 * math.Pi * math.Pi
)

type Body struct {
    x, y, z    float64
    vx, vy, vz float64
    m          float64
}

func main() {
    steps := int64(50000000)
    if len(os.Args) > 1 {
        if s, err := strconv.ParseInt(os.Args[1], 10, 64); err == nil {
            steps = s
        }
    }
    dt := 0.01 // time step (years). Adjust if needed.

    // Initialize bodies (Sun, Jupiter, Saturn, Uranus, Neptune)
    bodies := []Body{
        {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, SOLAR_MASS},
        {4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01,
            1.66007664274403694e-03 * DAYS_PER_YEAR, 7.69901118419740425e-03 * DAYS_PER_YEAR, -6.90460016972063023e-05 * DAYS_PER_YEAR,
            9.54791938424326609e-04 * SOLAR_MASS},
        {8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01,
            -2.76742510726862411e-03 * DAYS_PER_YEAR, 4.99852801234917238e-03 * DAYS_PER_YEAR, 2.30417297573763929e-05 * DAYS_PER_YEAR,
            2.85885980666130812e-04 * SOLAR_MASS},
        {1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01,
            2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR, -2.96589568540237556e-05 * DAYS_PER_YEAR,
            4.36624404335156298e-05 * SOLAR_MASS},
        {1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01,
            2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR, -9.51592254519715870e-05 * DAYS_PER_YEAR,
            5.15138902046611451e-05 * SOLAR_MASS},
    }

    // Offset momentum so center of mass is stationary
    var px, py, pz float64
    for i := range bodies {
        px += bodies[i].vx * bodies[i].m
        py += bodies[i].vy * bodies[i].m
        pz += bodies[i].vz * bodies[i].m
    }
    bodies[0].vx = -px / bodies[0].m
    bodies[0].vy = -py / bodies[0].m
    bodies[0].vz = -pz / bodies[0].m

    start := time.Now()

    // Pre-allocate locals to avoid allocations in loop
    n := len(bodies)
    for step := int64(0); step < steps; step++ {
        // velocity updates (pairwise)
        for i := 0; i < n; i++ {
            for j := i + 1; j < n; j++ {
                dx := bodies[i].x - bodies[j].x
                dy := bodies[i].y - bodies[j].y
                dz := bodies[i].z - bodies[j].z
                dist2 := dx*dx + dy*dy + dz*dz
                dist := math.Sqrt(dist2)
                // avoid division by zero; with real ephemeris this won't happen
                mag := dt / (dist * dist2)
                mi := bodies[i].m
                mj := bodies[j].m

                // update velocities
                bodies[i].vx -= dx * mj * mag
                bodies[i].vy -= dy * mj * mag
                bodies[i].vz -= dz * mj * mag

                bodies[j].vx += dx * mi * mag
                bodies[j].vy += dy * mi * mag
                bodies[j].vz += dz * mi * mag
            }
        }

        // position updates
        for i := 0; i < n; i++ {
            bodies[i].x += dt * bodies[i].vx
            bodies[i].y += dt * bodies[i].vy
            bodies[i].z += dt * bodies[i].vz
        }
    }

    elapsed := time.Since(start)
    fmt.Printf("Steps: %d, elapsed: %v\n", steps, elapsed)

    // compute total energy (optional)
    energy := totalEnergy(bodies)
    fmt.Printf("Energy: %.12f\n", energy)
}

func totalEnergy(bodies []Body) float64 {
    var e float64
    n := len(bodies)
    for i := 0; i < n; i++ {
        e += 0.5 * bodies[i].m * (bodies[i].vx*bodies[i].vx + bodies[i].vy*bodies[i].vy + bodies[i].vz*bodies[i].vz)
        for j := i + 1; j < n; j++ {
            dx := bodies[i].x - bodies[j].x
            dy := bodies[i].y - bodies[j].y
            dz := bodies[i].z - bodies[j].z
            dist := math.Sqrt(dx*dx + dy*dy + dz*dz)
            e -= (bodies[i].m * bodies[j].m) / dist
        }
    }
    return e
}
