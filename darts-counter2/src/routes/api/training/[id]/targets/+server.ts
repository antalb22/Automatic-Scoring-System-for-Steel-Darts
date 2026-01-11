import type {RequestHandler} from '@sveltejs/kit';
import db from '$lib/db/db';

export const POST: RequestHandler = async ({params, request}) => {
    const plan_id = Number(params.id);
    const data = await request.json();

    const row = db.prepare('SELECT MAX("order") as o FROM training_plan_target WHERE plan_id=?').get(plan_id) as {
        o: number
    } | undefined;
    const lastOrder = row?.o ?? 0;

    const stmt = db.prepare('INSERT INTO training_plan_target (plan_id,"order",value,type) VALUES (?,?,?,?)');
    const info = stmt.run(plan_id, lastOrder + 1, data.value, data.type);

    return new Response(JSON.stringify({
        id: info.lastInsertRowid,
        order: lastOrder + 1,
        value: data.value,
        type: data.type
    }));
};
