import type {RequestHandler} from '@sveltejs/kit';
import db from '$lib/db/db';
import dayjs from 'dayjs';

export const POST: RequestHandler = async ({request}) => {
    const body = await request.json();

    const player1 = body.player1;
    const player2 = body.player2 ?? null;
    const mode = body.mode ?? 501;
    const doubleOut = body.doubleOut ?? true;
    const autoGame = body.autoGame ?? false;

    const trainingPlanId = body.trainingPlanId ?? null;

    if (!player1 || typeof player1 !== 'string') {
        return new Response(JSON.stringify({success: false, error: 'player1 is required'}), {
            status: 400
        });
    }

    const startedAt = dayjs().format('YYYY-MM-DD HH:mm:ss');

    const stmt = db.prepare(`
        INSERT INTO game (player1, player2, mode, double_out, auto, training_plan_id, started_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    const info = stmt.run(
        player1,
        player2,
        mode,
        doubleOut ? 1 : 0,
        autoGame ? 1 : 0,
        trainingPlanId,
        startedAt
    );

    return new Response(JSON.stringify({
        success: true,
        id: info.lastInsertRowid
    }), {
        headers: {'Content-Type': 'application/json'},
        status: 200
    });
};