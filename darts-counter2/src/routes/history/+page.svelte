<script lang="ts">
    import {onMount} from 'svelte';
    import Navbar from '$lib/components/Navbar.svelte';
    import GameCard from '$lib/components/GameCard.svelte';

    interface Game {
        id: number;
        player1: string;
        player2: string | null;
        mode: number;
        double_out: boolean;
        started_at: string;
        finished: number;
        winner: string;
    }

    let games: Game[] = [];

    onMount(async () => {
        const res = await fetch('/api/game');
        const data = await res.json();
        if (data.success) {
            games = data.games;
        }
    });
</script>

<Navbar/>

<main>
    <h1>Game History</h1>

    {#if games.length > 0}
        {#each games as game}
            <GameCard {game}/>
        {/each}
    {:else}
        <p>No games yet.</p>
    {/if}
</main>
