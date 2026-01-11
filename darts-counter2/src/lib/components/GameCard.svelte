<script lang="ts">
    export let game: {
        id: number;
        player1: string;
        player2: string | null;
        mode: number;
        double_out: boolean;
        started_at: string;
        finished: number;
        winner: string;
    };
</script>

<div class="game">
    <h2>{game.player1} vs {game.player2 ?? '---'}</h2>
    <p>Mode: {game.mode}</p>
    <p>Double Out: {game.double_out ? 'Yes' : 'No'}</p>
    <p>Started: {game.started_at}</p>
    <p>
        {#if game.finished}
            Winner: {game.winner}
        {:else}
            Game not finished
        {/if}
    </p>
</div>

<style>
    .game {
        border: 1px solid #ccc;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 8px;
    }
</style>
