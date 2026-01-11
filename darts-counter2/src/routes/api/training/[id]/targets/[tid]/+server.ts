import type {RequestHandler} from '@sveltejs/kit';
import db from '$lib/db/db';

//Adott target törlése egy terven belül
export const DELETE: RequestHandler = ({params}) => {
    const tid = Number(params.tid);
    db.prepare('DELETE FROM training_plan_target WHERE id=?').run(tid);
    return new Response(JSON.stringify({success: true}));
};
