import {calculateDartScore} from "$lib/utils/dartScore";

const SECTORS = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5];

export function calculateSpread(throws: any[]): { sigmaX: number, sigmaY: number, count: number } {
    const validThrows = throws.filter(t =>
        t.x !== undefined && t.y !== undefined &&
        t.targetX !== undefined && t.targetY !== undefined
    );

    if (validThrows.length < 5) return {sigmaX: 2.5, sigmaY: 2.5, count: validThrows.length};

    let sumSqX = 0;
    let sumSqY = 0;

    validThrows.forEach(t => {
        const dx = t.x - t.targetX;
        const dy = t.y - t.targetY;
        sumSqX += dx * dx;
        sumSqY += dy * dy;
    });

    const sigmaX = Math.sqrt(sumSqX / validThrows.length);
    const sigmaY = Math.sqrt(sumSqY / validThrows.length);

    return {sigmaX, sigmaY, count: validThrows.length};
}

export function calculateExpectedValue(aimX: number, aimY: number, sigmaX: number, sigmaY: number): number {
    const limitX = 3 * sigmaX;
    const limitY = 3 * sigmaY;
    const step = 0.2;

    let totalWeightedScore = 0;
    let totalProbability = 0;

    const factorX = 1 / (sigmaX * Math.sqrt(2 * Math.PI));
    const factorY = 1 / (sigmaY * Math.sqrt(2 * Math.PI));

    for (let dx = -limitX; dx <= limitX; dx += step) {
        const probX = factorX * Math.exp(-(dx * dx) / (2 * sigmaX * sigmaX));

        for (let dy = -limitY; dy <= limitY; dy += step) {
            const probY = factorY * Math.exp(-(dy * dy) / (2 * sigmaY * sigmaY));
            const prob = probX * probY;

            const landingX = aimX + dx;
            const landingY = aimY + dy;

            const result = calculateDartScore(landingX, landingY);

            totalWeightedScore += result.score * prob;
            totalProbability += prob;
        }
    }

    return totalWeightedScore / totalProbability;
}

export function findOptimalTarget(sigmaX: number, sigmaY: number): {
    x: number,
    y: number,
    name: string,
    ev: number,
    label: string
} {

    const candidates = [
        {x: 0, y: 0, name: "Bullseye"}
    ];

    const R_TRIPLE = 10.3;

    SECTORS.forEach((sectorValue, index) => {

        const angleDeg = 90 - (index * 18);
        const angleRad = angleDeg * (Math.PI / 180);

        candidates.push({
            x: R_TRIPLE * Math.cos(angleRad),
            y: R_TRIPLE * Math.sin(angleRad),
            name: `T${sectorValue}`
        });
    });

    for (let y = 6; y <= 12; y += 0.5) {
        if (Math.abs(y - 10.3) < 0.1) continue;

        candidates.push({
            x: 0,
            y: y,
            name: `20 (Y=${y}cm)`
        });
    }

    let best = {x: 0, y: 0, name: "", ev: 0};

    candidates.forEach(cand => {
        const ev = calculateExpectedValue(cand.x, cand.y, sigmaX, sigmaY);
        if (ev > best.ev) {
            best = {x: cand.x, y: cand.y, name: cand.name, ev: ev};
        }
    });

    const bestResult = calculateDartScore(best.x, best.y);

    return {
        x: best.x,
        y: best.y,
        name: best.name,
        ev: best.ev,
        label: bestResult.area
    };
}