import db from '$lib/db/db';
import {json, type RequestHandler} from '@sveltejs/kit';

type Game = {
    id: number;
    training_plan_id: number | null;
    [key: string]: any;
};

export const GET: RequestHandler = async ({params}) => {
    const id = params.id;

    const stmt = db.prepare(`
        SELECT g.*, tp.name as plan_name
        FROM game g
                 LEFT JOIN training_plan tp ON g.training_plan_id = tp.id
        WHERE g.id = ?
    `);

    const game = stmt.get(id) as Game | undefined;

    if (!game) {
        return json({error: 'Game not found'}, {status: 404});
    }

    let targets: any[] = [];

    if (game.training_plan_id) {
        const targetsStmt = db.prepare(`
            SELECT *
            FROM training_plan_target
            WHERE plan_id = ?
            ORDER BY "order" ASC
        `);
        targets = targetsStmt.all(game.training_plan_id);
    }

    const throwsStmt = db.prepare(`
        SELECT *
        FROM throw
        WHERE game_id = ?
        ORDER BY created_at ASC
    `);
    const throws = throwsStmt.all(id);

    return new Response(JSON.stringify({
        success: true,
        game,
        targets,
        throws
    }), {
        headers: {'Content-Type': 'application/json'},
        status: 200
    });
};