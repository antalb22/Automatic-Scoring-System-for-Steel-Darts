import type {PageLoad} from './$types';

export const load: PageLoad = async ({fetch, params}) => {
    const res = await fetch(`/api/game/${params.id}`);
    const gameData = await res.json();

    const autoRes = await fetch(`/api/autothrows`);
    const autoData = await autoRes.json();

    return {
        game: gameData.game,
        targets: gameData.targets || [],
        throws: gameData.throws || [],
        autoThrow: autoData.success ? autoData.throw : null
    };
};