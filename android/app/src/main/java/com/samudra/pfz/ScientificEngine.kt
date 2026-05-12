package com.samudra.pfz

import android.util.Log
import kotlin.math.floor
import kotlin.math.sqrt

/**
 * SAMUDRA AI — Scientific Core (Kotlin Native)
 * world-class performance for oceanographic data processing.
 */
class ScientificEngine {

    /**
     * High-speed Bilinear Interpolation for SST/Current Grids.
     * Replaces JS implementation for 10x faster particle advection.
     */
    fun interpolateGrid(grid: Array<FloatArray>, x: Float, y: Float): Float {
        val x0 = floor(x).toInt()
        val x1 = x0 + 1
        val y0 = floor(y).toInt()
        val y1 = y0 + 1

        val height = grid.size
        val width = if (height > 0) grid[0].size else 0

        if (x0 < 0 || x1 >= width || y0 < 0 || y1 >= height) return 0f

        val dx = x - x0
        val dy = y - y0

        val v00 = grid[y0][x0]
        val v10 = grid[y0][x1]
        val v01 = grid[y1][x0]
        val v11 = grid[y1][x1]

        return v00 * (1 - dx) * (1 - dy) +
               v10 * dx * (1 - dy) +
               v01 * (1 - dx) * dy +
               v11 * dx * dy
    }

    /**
     * Sobel-based Thermal Front Detection.
     * Analyzes SST gradients to find aggregation zones.
     */
    fun calculateFrontMagnitude(grid: Array<FloatArray>, x: Int, y: Int): Float {
        if (x <= 0 || x >= grid[0].size - 1 || y <= 0 || y >= grid.size - 1) return 0f

        // Sobel kernels for horizontal and vertical gradients
        val gx = (grid[y-1][x+1] + 2*grid[y][x+1] + grid[y+1][x+1]) -
                 (grid[y-1][x-1] + 2*grid[y][x-1] + grid[y+1][x-1])

        val gy = (grid[y+1][x-1] + 2*grid[y+1][x] + grid[y+1][x+1]) -
                 (grid[y-1][x-1] + 2*grid[y-1][x] + grid[y-1][x+1])

        return sqrt((gx * gx + gy * gy).toDouble()).toFloat()
    }
}
