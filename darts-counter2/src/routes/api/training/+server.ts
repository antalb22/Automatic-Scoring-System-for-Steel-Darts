import type {RequestHandler} from '@sveltejs/kit';
import db from '$lib/db/db';

export const GET: RequestHandler = async () => {
    const plans = db.prepare('SELECT id, name FROM training_plan').all();
    return new Response(JSON.stringify(plans), {status: 200});
};

export const POST: RequestHandler = async ({request}) => {
    const {name} = await request.json();
    if (!name) return new Response(JSON.stringify({error: 'Name required'}), {status: 400});

    const stmt = db.prepare('INSERT INTO training_plan (name) VALUES (?)');
    const info = stmt.run(name);
    return new Response(JSON.stringify({id: info.lastInsertRowid, name}), {status: 201});
};
