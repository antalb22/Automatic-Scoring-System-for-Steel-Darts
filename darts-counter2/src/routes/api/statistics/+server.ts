import db from '$lib/db/db';
import {json, type RequestHandler} from '@sveltejs/kit';

type Game = {
    id: number;
    player1: string;
    player2: string | null;
    finished: number;
    winner: string | null;
    mode: number;
};

type Throw = {
    id: number;
    game_id: number;
    player_id: number;
    points: number;
    distance: number | null;
    is_checkout: number;
};

export const GET: RequestHandler = () => {
    const games = db.prepare(`
        SELECT id, player1, player2, finished, winner, mode
        FROM game
        WHERE finished = 1
    `).all() as Game[];

    const playerMap: Record<string, string> = {};
    const gameModeMap: Record<number, number> = {};

    for (const game of games) {
        if (game.player1) playerMap[`${game.id}-1`] = game.player1;
        if (game.player2) playerMap[`${game.id}-2`] = game.player2;
        gameModeMap[game.id] = game.mode;
    }

    const lastThrowRows = db.prepare(`
        SELECT MAX(id) as id
        FROM throw
        GROUP BY game_id
    `).all() as { id: number }[];
    const winningThrowIds = new Set(lastThrowRows.map(r => r.id));

    const throws = db.prepare(`
        SELECT t.id, t.game_id, t.player_id, t.points, t.distance, t.is_checkout
        FROM throw t
                 JOIN game g ON t.game_id = g.id
        WHERE g.finished = 1
        ORDER BY t.game_id, t.id ASC
    `).all() as Throw[];

    const statsMap: Record<string, {
        gamesFinished: number;
        wins: number;
        totalPoints: number;
        throws: number;
        first9Points: number;
        first9Throws: number;
        checkoutAttempts: number;
        checkoutHits: number;
        totalDistance: number;
        throwsWithDistance: number;
    }> = {};

    const gameThrowCounts: Record<string, number> = {};

    for (const t of throws) {
        const key = `${t.game_id}-${t.player_id}`;
        const player = playerMap[key];

        if (!player) continue;

        if (!statsMap[player]) {
            statsMap[player] = {
                gamesFinished: 0, wins: 0,
                totalPoints: 0, throws: 0,
                first9Points: 0, first9Throws: 0,
                checkoutAttempts: 0, checkoutHits: 0,
                totalDistance: 0, throwsWithDistance: 0
            };
        }

        const s = statsMap[player];
        const mode = gameModeMap[t.game_id];

        const isCompetitive = mode === 301 || mode === 501;

        if (t.distance !== null) {
            s.totalDistance += t.distance;
            s.throwsWithDistance += 1;
        }

        if (isCompetitive) {
            s.totalPoints += t.points;
            s.throws += 1;

            if (!gameThrowCounts[key]) gameThrowCounts[key] = 0;
            gameThrowCounts[key]++;

            if (gameThrowCounts[key] <= 9) {
                s.first9Points += t.points;
                s.first9Throws += 1;
            }

            if (t.is_checkout === 1) {
                s.checkoutAttempts++;
                if (winningThrowIds.has(t.id)) {
                    s.checkoutHits++;
                }
            }
        }
    }

    for (const player of Object.keys(statsMap)) {
        const competitiveGames = games.filter(
            g => (g.player1 === player || g.player2 === player) &&
                (g.mode === 301 || g.mode === 501)
        );

        statsMap[player].gamesFinished = competitiveGames.length;
        statsMap[player].wins = competitiveGames.filter(g => g.winner === player).length;
    }

    const stats = Object.entries(statsMap).map(([player, data]) => {
        return {
            player,
            gamesFinished: data.gamesFinished,
            wins: data.wins,
            averageScore: data.throws > 0 ? (data.totalPoints / data.throws) * 3 : 0,
            averageAccuracy: data.throwsWithDistance > 0 ? (data.totalDistance / data.throwsWithDistance) : null,
            first9Average: data.first9Throws > 0 ? (data.first9Points / data.first9Throws) * 3 : 0,
            checkoutPercentage: data.checkoutAttempts > 0 ? (data.checkoutHits / data.checkoutAttempts) * 100 : 0
        };
    });

    return json(stats);
}