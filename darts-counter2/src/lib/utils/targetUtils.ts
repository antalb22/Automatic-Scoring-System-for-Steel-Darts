export const DARTBOARD_NUMBERS = [
    6, 13, 4, 18, 1, 20, 5, 12, 9, 14,
    11, 8, 16, 7, 19, 3, 17, 2, 15, 10
];

const RADII: Record<string, number> = {
    B: 0,
    OB: 0,
    S: 9.0,
    D: 17.0,
    T: 10.5
};

export function getTargetCoordinates(value: number, type: string): { x: number; y: number } {
    if (value === 25 || value === 50 || type === 'B' || type === 'OB') {
        return {x: 0, y: 0};
    }

    const segmentIndex = DARTBOARD_NUMBERS.indexOf(value);
    if (segmentIndex === -1) return {x: 0, y: 0};

    const anglePerSegment = 18;
    const angleDeg = segmentIndex * anglePerSegment;
    const angleRad = angleDeg * (Math.PI / 180);

    const r = RADII[type] || RADII.S;

    return {
        x: Math.cos(angleRad) * r,
        y: Math.sin(angleRad) * r
    };
}

export function getDistance(x1: number, y1: number, x2: number, y2: number): number {
    return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
}