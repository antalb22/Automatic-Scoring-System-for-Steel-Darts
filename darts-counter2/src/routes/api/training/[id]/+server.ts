import type {RequestHandler} from '@sveltejs/kit';
import db from '$lib/db/db';

export const GET: RequestHandler = async ({params}) => {
    const id = Number(params.id);

    const plan = db.prepare(`
        SELECT id, name
        FROM training_plan
        WHERE id = ?
    `).get(id);

    if (!plan) {
        return new Response(JSON.stringify({error: "Not found"}), {status: 404});
    }

    const targets = db.prepare(`
        SELECT id, value, type, "order"
        FROM training_plan_target
        WHERE plan_id = ?
        ORDER BY "order"
    `).all(id);

    return new Response(JSON.stringify({...plan, targets}), {status: 200});
};

export const DELETE: RequestHandler = async ({params}) => {
    const id = Number(params.id);

    db.prepare(`DELETE
                FROM training_plan
                WHERE id = ?`).run(id);

    return new Response(JSON.stringify({success: true}), {status: 200});
};
