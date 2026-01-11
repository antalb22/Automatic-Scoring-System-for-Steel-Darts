import {json} from '@sveltejs/kit';

let latestAutoThrow: any = null;
let lastSentId: any = null;

export const POST = async ({request}) => {
    const data = await request.json();
    latestAutoThrow = {
        ...data,
        created_at: new Date().toISOString()
    };
    return json({success: true});
};

export const GET = async () => {
    if (!latestAutoThrow) {
        return json({success: false, throw: null});
    }

    if (latestAutoThrow.throwId === lastSentId) {
        return json({success: false, throw: null});
    }

    lastSentId = latestAutoThrow.throwId;
    return json({success: true, throw: latestAutoThrow});
};

