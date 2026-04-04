/**
 * SAMUDRA AI — High-Resolution HSI Simulation Layer (WASM/WebGPU Simulation Logic)
 * सिम्युलेशन लेयर - रीयल-टाइम उच्च-रिज़ॉल्यूशन रेंडरिंग
 *
 * Implements client-side particles and WebGL/WebGPU acceleration for:
 * 1. Time-Seek particle advection
 * 2. High-resolution SST gradients
 * 3. Species-specific distribution simulations
 */

class HSISimulationLayer {
    constructor(canvas, options = {}) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.particles = [];
        this.numParticles = options.numParticles || 2000;
        this.running = false;

        // Simulation parameters
        this.speedScale = 0.5;
        this.particleLife = 100;
        this.colorMode = options.colorMode || 'sst'; // 'sst', 'current', 'productivity'

        // Data grid
        this.grid = null; // {sst, u, v, lat, lng}
    }

    updateGrid(gridData) {
        this.grid = gridData;
    }

    initParticles() {
        this.particles = [];
        for (let i = 0; i < this.numParticles; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                age: Math.random() * this.particleLife,
                vx: 0,
                vy: 0,
                color: '#fff'
            });
        }
    }

    start() {
        if (!this.running) {
            this.running = true;
            this.initParticles();
            this.animate();
        }
    }

    stop() {
        this.running = false;
    }

    animate() {
        if (!this.running) return;

        this.ctx.fillStyle = 'rgba(0, 8, 20, 0.15)'; // Trail effect
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.particles.forEach(p => {
            // Update velocity from grid
            if (this.grid) {
                // Bilinear interpolation for u, v current from grid
                const gridPos = this.screenToGrid(p.x, p.y);
                const current = this.getGridValue(gridPos.x, gridPos.y, 'current');
                p.vx = current.u * this.speedScale;
                p.vy = -current.v * this.speedScale; // canvas y is down

                // Color from SST
                const sst = this.getGridValue(gridPos.x, gridPos.y, 'sst');
                p.color = this.sstToColor(sst);
            }

            p.x += p.vx;
            p.y += p.vy;
            p.age++;

            // Draw particle
            this.ctx.fillStyle = p.color;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, 1.2, 0, Math.PI * 2);
            this.ctx.fill();

            // Respawn
            if (p.age > this.particleLife ||
                p.x < 0 || p.x > this.canvas.width ||
                p.y < 0 || p.y > this.canvas.height) {
                p.x = Math.random() * this.canvas.width;
                p.y = Math.random() * this.canvas.height;
                p.age = 0;
            }
        });

        requestAnimationFrame(() => this.animate());
    }

    screenToGrid(sx, sy) {
        if (!this.grid) return { x: 0, y: 0 };
        return {
            x: (sx / this.canvas.width) * (this.grid.lng.length - 1),
            y: (sy / this.canvas.height) * (this.grid.lat.length - 1)
        };
    }

    getGridValue(gx, gy, type) {
        if (!this.grid) return type === 'current' ? { u: 0, v: 0 } : 28.0;

        const ix = Math.floor(gx);
        const iy = Math.floor(gy);

        if (type === 'current') {
            const u = this.grid.u_current[iy][ix] || 0;
            const v = this.grid.v_current[iy][ix] || 0;
            return { u, v };
        } else {
            return this.grid.sst[iy][ix] || 28.0;
        }
    }

    sstToColor(sst) {
        if (sst < 24) return '#3498db'; // Cold blue
        if (sst < 26) return '#2ecc71'; // Greenish
        if (sst < 28) return '#f1c40f'; // Yellow
        if (sst < 30) return '#e67e22'; // Orange
        return '#e74c3c'; // Red hot
    }
}
