export type DartScoreResult = {
    points: number;
    multiplier: number;
    score: number;
    area: string;
};

export function calculateDartScore(x: number, y: number): DartScoreResult {
    const BOARD_RADIUS = 17;
    const BULLSEYE_RADIUS = 0.635;
    const OUTER_BULL_RADIUS = 1.6;
    const TRIPLE_RING_INNER = 9.9;
    const TRIPLE_RING_OUTER = 10.7;
    const DOUBLE_RING_INNER = 16.2;
    const DOUBLE_RING_OUTER = 17;

    const ANGLE_PER_SECTION = 18;
    const DARTBOARD_NUMBERS = [
        6, 13, 4, 18, 1, 20, 5, 12, 9, 14,
        11, 8, 16, 7, 19, 3, 17, 2, 15, 10
    ];

    const distance = Math.sqrt(x * x + y * y);
    let angle = Math.atan2(y, x) * (180 / Math.PI);
    if (angle < 0) angle += 360;

    if (distance <= BULLSEYE_RADIUS) {
        return {
            points: 50,
            multiplier: 2,
            score: 50,
            area: "BULL"
        };
    }

    if (distance <= OUTER_BULL_RADIUS) {
        return {
            points: 25,
            multiplier: 1,
            score: 25,
            area: "OUTER_BULL"
        };
    }

    const segmentIndex =
        Math.floor((angle + ANGLE_PER_SECTION / 2) / ANGLE_PER_SECTION) % 20;
    const base = DARTBOARD_NUMBERS[segmentIndex];

    if (distance >= TRIPLE_RING_INNER && distance <= TRIPLE_RING_OUTER) {
        return {
            points: base,
            multiplier: 3,
            score: base * 3,
            area: `T${base}`
        };
    }

    if (distance >= DOUBLE_RING_INNER && distance <= DOUBLE_RING_OUTER) {
        return {
            points: base,
            multiplier: 2,
            score: base * 2,
            area: `D${base}`
        };
    }

    if (distance > BOARD_RADIUS) {
        return {
            points: 0,
            multiplier: 0,
            score: 0,
            area: "MISS"
        };
    }

    return {
        points: base,
        multiplier: 1,
        score: base,
        area: `S${base}`
    };
}
