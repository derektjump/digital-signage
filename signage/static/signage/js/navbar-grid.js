/**
 * Interactive Mouse-Reactive Grid Background
 * Creates a Tron-like grid with chromatic aberration glow effect
 * Part of The Grid Design System
 */

(function() {
    'use strict';

    const canvas = document.getElementById('navbar-grid-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const container = canvas.parentElement;

    // Configuration
    const config = {
        cellSize: 50,
        baseAlpha: 0.02,
        glowRadius: 150,
        influenceRadius: 300,
        lineWidth: 1,
        colors: {
            verticalLeft: 'rgba(255,59,129,',    // Pink
            verticalRight: 'rgba(0,240,255,',    // Cyan
            horizontalAbove: 'rgba(100,52,248,', // Purple
            horizontalBelow: 'rgba(255,255,255,' // White
        }
    };

    let mouseX = null, mouseY = null, isMouseInside = false;
    let animationFrameId = null, previousWidth = 0;

    function resizeCanvas() {
        const rect = container.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = rect.height;
        previousWidth = rect.width;

        // Smaller cells for collapsed nav
        if (rect.width < 100) {
            config.cellSize = 30;
            config.glowRadius = 100;
            config.influenceRadius = 200;
        } else {
            config.cellSize = 50;
            config.glowRadius = 150;
            config.influenceRadius = 300;
        }
        drawGrid();
    }

    function drawGrid() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.lineWidth = config.lineWidth;

        const { cellSize, baseAlpha, glowRadius, influenceRadius, colors } = config;

        // Vertical lines
        for (let x = 0; x <= canvas.width; x += cellSize) {
            const dx = mouseX !== null ? x - mouseX : null;
            let distanceFactor = 0;

            if (mouseX !== null && mouseY !== null && isMouseInside) {
                distanceFactor = Math.max(0, 1 - Math.abs(dx) / influenceRadius);
            }

            // Base line
            const alpha = baseAlpha + distanceFactor * 0.04;
            ctx.strokeStyle = `rgba(255,255,255,${alpha.toFixed(3)})`;
            ctx.beginPath();
            ctx.moveTo(x + 0.5, 0);
            ctx.lineTo(x + 0.5, canvas.height);
            ctx.stroke();

            // Glow segment
            if (mouseX !== null && mouseY !== null && isMouseInside && distanceFactor > 0) {
                let chromaIntensity = distanceFactor * 0.25;
                if (Math.abs(dx) < cellSize * 0.5) chromaIntensity = Math.min(0.6, chromaIntensity * 2);

                const yStart = Math.max(0, mouseY - glowRadius);
                const yEnd = Math.min(canvas.height, mouseY + glowRadius);
                const color = dx < 0 ? colors.verticalLeft : colors.verticalRight;

                const grad = ctx.createLinearGradient(0, yStart, 0, yEnd);
                const mid = Math.max(0, Math.min(1, (mouseY - yStart) / (yEnd - yStart)));

                grad.addColorStop(0.0, color + '0)');
                if (mid - 0.15 > 0) grad.addColorStop(mid - 0.15, color + (chromaIntensity * 0.3).toFixed(3) + ')');
                if (mid - 0.05 > 0) grad.addColorStop(mid - 0.05, color + (chromaIntensity * 0.8).toFixed(3) + ')');
                grad.addColorStop(mid, color + chromaIntensity.toFixed(3) + ')');
                if (mid + 0.05 < 1) grad.addColorStop(mid + 0.05, color + (chromaIntensity * 0.8).toFixed(3) + ')');
                if (mid + 0.15 < 1) grad.addColorStop(mid + 0.15, color + (chromaIntensity * 0.3).toFixed(3) + ')');
                grad.addColorStop(1.0, color + '0)');

                ctx.strokeStyle = grad;
                ctx.beginPath();
                ctx.moveTo(x + 0.5, yStart);
                ctx.lineTo(x + 0.5, yEnd);
                ctx.stroke();
            }
        }

        // Horizontal lines
        for (let y = 0; y <= canvas.height; y += cellSize) {
            const dy = mouseY !== null ? y - mouseY : null;
            let distanceFactor = 0;

            if (mouseX !== null && mouseY !== null && isMouseInside) {
                distanceFactor = Math.max(0, 1 - Math.abs(dy) / (cellSize * 4));
            }

            const alpha = baseAlpha + distanceFactor * 0.04;
            ctx.strokeStyle = `rgba(255,255,255,${alpha.toFixed(3)})`;
            ctx.beginPath();
            ctx.moveTo(0, y + 0.5);
            ctx.lineTo(canvas.width, y + 0.5);
            ctx.stroke();

            if (mouseX !== null && mouseY !== null && isMouseInside && distanceFactor > 0) {
                let chromaIntensity = distanceFactor * 0.25;
                if (Math.abs(dy) < cellSize * 0.5) chromaIntensity = Math.min(0.6, chromaIntensity * 2);

                const xStart = Math.max(0, mouseX - glowRadius);
                const xEnd = Math.min(canvas.width, mouseX + glowRadius);
                const color = dy < 0 ? colors.horizontalAbove : colors.horizontalBelow;
                let maxAlpha = chromaIntensity;
                if (dy >= 0) maxAlpha *= 0.5;

                const grad = ctx.createLinearGradient(xStart, 0, xEnd, 0);
                const mid = Math.max(0, Math.min(1, (mouseX - xStart) / (xEnd - xStart)));

                grad.addColorStop(0.0, color + '0)');
                if (mid - 0.15 > 0) grad.addColorStop(mid - 0.15, color + (maxAlpha * 0.3).toFixed(3) + ')');
                if (mid - 0.05 > 0) grad.addColorStop(mid - 0.05, color + (maxAlpha * 0.8).toFixed(3) + ')');
                grad.addColorStop(mid, color + maxAlpha.toFixed(3) + ')');
                if (mid + 0.05 < 1) grad.addColorStop(mid + 0.05, color + (maxAlpha * 0.8).toFixed(3) + ')');
                if (mid + 0.15 < 1) grad.addColorStop(mid + 0.15, color + (maxAlpha * 0.3).toFixed(3) + ')');
                grad.addColorStop(1.0, color + '0)');

                ctx.strokeStyle = grad;
                ctx.beginPath();
                ctx.moveTo(xStart, y + 0.5);
                ctx.lineTo(xEnd, y + 0.5);
                ctx.stroke();
            }
        }
    }

    function animate() {
        const currentWidth = container.offsetWidth;
        if (Math.abs(currentWidth - previousWidth) > 10) resizeCanvas();
        drawGrid();
        animationFrameId = requestAnimationFrame(animate);
    }

    function handleMouseMove(e) {
        const rect = container.getBoundingClientRect();
        if (e.clientX >= rect.left && e.clientX <= rect.right &&
            e.clientY >= rect.top && e.clientY <= rect.bottom) {
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
            isMouseInside = true;
        } else {
            isMouseInside = false;
        }
    }

    // Initialize
    window.addEventListener('resize', () => setTimeout(resizeCanvas, 150));
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseleave', () => { isMouseInside = false; });

    // Handle collapse button
    document.querySelector('.collapse-expand-btn')?.addEventListener('click', () => {
        setTimeout(resizeCanvas, 50);
    });

    setTimeout(() => {
        if (container.offsetWidth > 0) {
            resizeCanvas();
            animate();
        }
    }, 50);
})();
