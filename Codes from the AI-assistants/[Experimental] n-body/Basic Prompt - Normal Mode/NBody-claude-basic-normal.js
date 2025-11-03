import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';

const JovianNBodySimulation = () => {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const animationRef = useRef(null);
  const [isRunning, setIsRunning] = useState(false);
  const [timeScale, setTimeScale] = useState(1);
  const [showTrails, setShowTrails] = useState(true);

  // Physical constants (scaled for simulation)
  const G = 6.67430e-11; // Gravitational constant
  const AU = 1.496e11; // Astronomical unit in meters
  const SCALE = 1e-9; // Scale factor for visualization
  const TIME_SCALE = 86400; // 1 day per simulation step

  // Celestial bodies data (masses in kg, distances in AU, scaled)
  const bodies = [
    {
      name: 'Sun',
      mass: 1.989e30,
      position: [0, 0, 0],
      velocity: [0, 0, 0],
      color: 0xffff00,
      size: 0.5,
      trail: []
    },
    {
      name: 'Jupiter',
      mass: 1.898e27,
      position: [5.2 * AU * SCALE, 0, 0],
      velocity: [0, 0, 13070 * SCALE],
      color: 0xffa500,
      size: 0.3,
      trail: []
    },
    {
      name: 'Io',
      mass: 8.932e22,
      position: [5.2 * AU * SCALE + 421700000 * SCALE, 0, 0],
      velocity: [0, 0, 13070 * SCALE + 17334 * SCALE],
      color: 0xffff99,
      size: 0.05,
      trail: []
    },
    {
      name: 'Europa',
      mass: 4.800e22,
      position: [5.2 * AU * SCALE + 671034000 * SCALE, 0, 0],
      velocity: [0, 0, 13070 * SCALE + 13743 * SCALE],
      color: 0x87ceeb,
      size: 0.04,
      trail: []
    },
    {
      name: 'Ganymede',
      mass: 1.482e23,
      position: [5.2 * AU * SCALE + 1070412000 * SCALE, 0, 0],
      velocity: [0, 0, 13070 * SCALE + 10880 * SCALE],
      color: 0x8b7d6b,
      size: 0.06,
      trail: []
    },
    {
      name: 'Callisto',
      mass: 1.076e23,
      position: [5.2 * AU * SCALE + 1882709000 * SCALE, 0, 0],
      velocity: [0, 0, 13070 * SCALE + 8204 * SCALE],
      color: 0x696969,
      size: 0.055,
      trail: []
    }
  ];

  // N-Body simulation using Verlet integration
  const updatePhysics = (dt) => {
    const n = bodies.length;
    const forces = Array(n).fill().map(() => [0, 0, 0]);
    
    // Calculate gravitational forces between all pairs
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        const dx = bodies[j].position[0] - bodies[i].position[0];
        const dy = bodies[j].position[1] - bodies[i].position[1];
        const dz = bodies[j].position[2] - bodies[i].position[2];
        
        const r2 = dx * dx + dy * dy + dz * dz;
        const r = Math.sqrt(r2);
        
        // Avoid singularities
        if (r < 1e-6) continue;
        
        const F = G * bodies[i].mass * bodies[j].mass / r2;
        const fx = F * dx / r;
        const fy = F * dy / r;
        const fz = F * dz / r;
        
        // Newton's third law
        forces[i][0] += fx;
        forces[i][1] += fy;
        forces[i][2] += fz;
        forces[j][0] -= fx;
        forces[j][1] -= fy;
        forces[j][2] -= fz;
      }
    }
    
    // Update positions and velocities using Verlet integration
    for (let i = 0; i < n; i++) {
      const body = bodies[i];
      const ax = forces[i][0] / body.mass;
      const ay = forces[i][1] / body.mass;
      const az = forces[i][2] / body.mass;
      
      // Update velocity (kick step)
      body.velocity[0] += ax * dt;
      body.velocity[1] += ay * dt;
      body.velocity[2] += az * dt;
      
      // Update position (drift step)
      body.position[0] += body.velocity[0] * dt;
      body.position[1] += body.velocity[1] * dt;
      body.position[2] += body.velocity[2] * dt;
      
      // Store trail points
      if (showTrails && body.trail.length < 500) {
        body.trail.push([...body.position]);
      } else if (showTrails && body.trail.length >= 500) {
        body.trail.shift();
        body.trail.push([...body.position]);
      }
    }
  };

  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000011);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(75, 800 / 600, 0.1, 1000);
    camera.position.set(0, 5, 15);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(800, 600);
    mountRef.current.appendChild(renderer.domElement);

    // Create celestial bodies
    const meshes = [];
    const trailLines = [];

    bodies.forEach((body, index) => {
      // Create sphere for body
      const geometry = new THREE.SphereGeometry(body.size, 16, 16);
      const material = new THREE.MeshBasicMaterial({ color: body.color });
      const mesh = new THREE.Mesh(geometry, material);
      scene.add(mesh);
      meshes.push(mesh);

      // Create trail line
      const trailGeometry = new THREE.BufferGeometry();
      const trailMaterial = new THREE.LineBasicMaterial({ 
        color: body.color, 
        opacity: 0.3, 
        transparent: true 
      });
      const trailLine = new THREE.Line(trailGeometry, trailMaterial);
      scene.add(trailLine);
      trailLines.push(trailLine);
    });

    // Add stars
    const starGeometry = new THREE.BufferGeometry();
    const starVertices = [];
    for (let i = 0; i < 1000; i++) {
      starVertices.push(
        (Math.random() - 0.5) * 200,
        (Math.random() - 0.5) * 200,
        (Math.random() - 0.5) * 200
      );
    }
    starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3));
    const starMaterial = new THREE.PointsMaterial({ color: 0xffffff, size: 0.1 });
    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);

    // Animation loop
    const animate = () => {
      if (!isRunning) {
        animationRef.current = requestAnimationFrame(animate);
        renderer.render(scene, camera);
        return;
      }

      // Update physics
      updatePhysics(TIME_SCALE * timeScale);

      // Update visual representation
      bodies.forEach((body, index) => {
        meshes[index].position.set(
          body.position[0],
          body.position[1],
          body.position[2]
        );

        // Update trails
        if (showTrails && body.trail.length > 1) {
          const trailVertices = [];
          body.trail.forEach(point => {
            trailVertices.push(point[0], point[1], point[2]);
          });
          trailLines[index].geometry.setAttribute(
            'position',
            new THREE.Float32BufferAttribute(trailVertices, 3)
          );
          trailLines[index].visible = true;
        } else {
          trailLines[index].visible = false;
        }
      });

      // Simple camera rotation
      const time = Date.now() * 0.0005;
      camera.position.x = Math.cos(time) * 20;
      camera.position.z = Math.sin(time) * 20;
      camera.lookAt(0, 0, 0);

      renderer.render(scene, camera);
      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [isRunning, timeScale, showTrails]);

  const resetSimulation = () => {
    // Reset positions and velocities to initial values
    bodies[0].position = [0, 0, 0];
    bodies[0].velocity = [0, 0, 0];
    
    bodies[1].position = [5.2 * AU * SCALE, 0, 0];
    bodies[1].velocity = [0, 0, 13070 * SCALE];
    
    bodies[2].position = [5.2 * AU * SCALE + 421700000 * SCALE, 0, 0];
    bodies[2].velocity = [0, 0, 13070 * SCALE + 17334 * SCALE];
    
    bodies[3].position = [5.2 * AU * SCALE + 671034000 * SCALE, 0, 0];
    bodies[3].velocity = [0, 0, 13070 * SCALE + 13743 * SCALE];
    
    bodies[4].position = [5.2 * AU * SCALE + 1070412000 * SCALE, 0, 0];
    bodies[4].velocity = [0, 0, 13070 * SCALE + 10880 * SCALE];
    
    bodies[5].position = [5.2 * AU * SCALE + 1882709000 * SCALE, 0, 0];
    bodies[5].velocity = [0, 0, 13070 * SCALE + 8204 * SCALE];

    // Clear trails
    bodies.forEach(body => {
      body.trail = [];
    });
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-gray-900 text-white rounded-lg">
      <h1 className="text-3xl font-bold mb-6 text-center">Jovian N-Body Orbital Simulation</h1>
      
      <div className="mb-4 flex flex-wrap gap-4 justify-center">
        <button
          onClick={() => setIsRunning(!isRunning)}
          className={`px-4 py-2 rounded font-semibold ${
            isRunning 
              ? 'bg-red-600 hover:bg-red-700' 
              : 'bg-green-600 hover:bg-green-700'
          }`}
        >
          {isRunning ? 'Pause' : 'Start'}
        </button>
        
        <button
          onClick={resetSimulation}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded font-semibold"
        >
          Reset
        </button>
        
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={showTrails}
            onChange={(e) => setShowTrails(e.target.checked)}
            className="w-4 h-4"
          />
          Show Trails
        </label>
      </div>

      <div className="mb-4 flex items-center justify-center gap-4">
        <label className="flex items-center gap-2">
          Time Scale:
          <input
            type="range"
            min="0.1"
            max="5"
            step="0.1"
            value={timeScale}
            onChange={(e) => setTimeScale(parseFloat(e.target.value))}
            className="w-32"
          />
          <span>{timeScale}x</span>
        </label>
      </div>

      <div 
        ref={mountRef} 
        className="w-full h-96 border border-gray-700 rounded mx-auto"
        style={{ maxWidth: '800px', height: '600px' }}
      />

      <div className="mt-4 text-sm">
        <h3 className="font-semibold mb-2">Legend:</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-yellow-400 rounded-full"></div>
            <span>Sun</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-orange-400 rounded-full"></div>
            <span>Jupiter</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-yellow-200 rounded-full"></div>
            <span>Io</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-blue-300 rounded-full"></div>
            <span>Europa</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-yellow-800 rounded-full"></div>
            <span>Ganymede</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-gray-500 rounded-full"></div>
            <span>Callisto</span>
          </div>
        </div>
      </div>

      <div className="mt-4 text-xs text-gray-400">
        <p>This simulation uses the Verlet integration method to solve the n-body problem for the Sun, Jupiter, and its four largest moons (Io, Europa, Ganymede, and Callisto). The gravitational forces between all bodies are calculated at each time step.</p>
      </div>
    </div>
  );
};

export default JovianNBodySimulation;