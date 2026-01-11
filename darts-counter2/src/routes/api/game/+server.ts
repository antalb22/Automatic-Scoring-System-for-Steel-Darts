import db from '$lib/db/db';
import {type RequestHandler} from '@sveltejs/kit';

export const GET: RequestHandler = async () => {
    const stmt = db.prepare('SELECT * FROM game ORDER BY id DESC');
    const games = stmt.all();

    return new Response(JSON.stringify({success: true, games}), {
        headers: {'Content-Type': 'application/json'},
        status: 200
    });
};
