import db from '$lib/db/db';
import type {RequestHandler} from '@sveltejs/kit';
import {json} from '@sveltejs/kit';

export const POST: RequestHandler = async ({request}) => {
    const {
        playerId, gameId, points, multiplier, isWinner = false, playerName,
        x, y, targetX, targetY, distance, expected_target,
        isCheckout
    } = await request.json();

    const stmt = db.prepare(`
        INSERT INTO throw (player_id, game_id, points, multiplier, x, y,
                           target_x, target_y, distance, expected_target, is_checkout)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
        playerId, gameId, points, multiplier,
        x ?? null, y ?? null, targetX ?? null, targetY ?? null, distance ?? null, expected_target ?? null,
        isCheckout ? 1 : 0
    );

    if (isWinner) {
        const update = db.prepare(`
            UPDATE game
            SET finished = 1,
                winner   = ?
            WHERE id = ?
        `);
        update.run(playerName, gameId);
    }

    return json({success: true});
}

export const DELETE: RequestHandler = async ({request}) => {
    const {gameId, playerId} = await request.json();

    const stmt = db.prepare(`
        DELETE
        FROM throw
        WHERE id = (SELECT id
                    FROM throw
                    WHERE game_id = ?
                      AND player_id = ?
                    ORDER BY created_at DESC
                    LIMIT 1)
    `);
    stmt.run(gameId, playerId);

    return json({success: true});
};
